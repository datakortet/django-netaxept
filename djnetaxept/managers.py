import logging
import suds
import requests
from djnetaxept.utils import MERCHANTID, TOKEN
from django.conf import settings
from django.db import models
from django.db.models import Q
from djnetaxept.credentials import Credentials
from djnetaxept.utils import get_client, get_basic_registerrequest, get_netaxept_object, handle_response_exception
from djnetaxept.operations import register, process, query, batch
from djnetaxept.exceptions import PaymentNotAuthorized, AmountAllreadyCaptured, NoAmountCaptured, ProcessException, \
    PaymentRegistrationNotCompleted

logger = logging.getLogger('djnetaxept.managers')


"""The merchantid and token should not be stored here, but rather in a secure vault.
For testing purposes, it can however be convenient to set them here. Just remember to
never use the token for production here in this file. (Test environment has its own 
token.
"""
if hasattr(settings, 'NETS_CTX'):
    NETS_CTX = settings.NETS_CTX
else:
    class CTX(Credentials):
        def __init__(self):
            merchantid = '12345'
            token = 'abc123'
            self.rest_url = 'https://test.epayment.nets.eu/Netaxept/'
            self.terminal = "https://epayment-test.bbs.no/Terminal/default.aspx"
            super(CTX, self).__init__(merchantid, token, self.rest_url)

    NETS_CTX = CTX()

MERCHANTID = NETS_CTX.merchantid
TOKEN = NETS_CTX.token
REST_URL = NETS_CTX.rest_url
TERMINAL = NETS_CTX.terminal
REGISTER_URL = NETS_CTX.rest_register
PROCESS_URL = NETS_CTX.rest_process
QUERY_URL = NETS_CTX.rest_query


class NetaxeptPaymentManager(models.Manager):
    def register_payment(self,
                         redirect_url=None,
                         amount=None,
                         currencycode=None,
                         ordernumber=None,
                         description=None):

        client = get_client()
        request = get_basic_registerrequest(client, redirect_url, None)

        order = get_netaxept_object(client, 'Order')
        order.Amount = amount  # store
        order.CurrencyCode = currencycode  # store
        order.OrderNumber = ordernumber  # store
        order.UpdateStoredPaymentInfo = None

        request.Order = order
        request.Description = description  # Store

        payment = self.model(
            amount=amount,
            currencycode=currencycode,
            ordernumber=ordernumber,
            description=description
        )

        try:
            response = register(client, request)
            payment.transaction_id = response.TransactionId
        except suds.WebFault as e:
            handle_response_exception(e, payment)
        finally:
            payment.save()

        return payment

    def query(self, payment):
        """Use Netaxept REST API to query a payment.
        Args:
            payment: The payment we want to check.

        Returns: The full response.content from the query.
        """

        url = settings.NETAXEPT_REST_QUERY
        response = requests.post(
            url,
            data={
                'merchantId': MERCHANTID,
                'token': TOKEN,
                'transactionId': payment.transaction_id
            }
        )
        return response.content


class NetaxeptTransactionManager(models.Manager):
    def sale_payment(self, payment, amount):

        if not payment.completed():
            raise PaymentRegistrationNotCompleted(payment, amount)

        client = get_client()
        operation = 'SALE'

        request = get_netaxept_object(client, 'ProcessRequest')
        request.Operation = operation
        request.TransactionId = payment.transaction_id
        request.TransactionAmount = amount

        transaction = self.model(
            payment=payment,
            transaction_id=payment.transaction_id,
            amount=amount,
            operation=operation,
        )

        try:
            response = process(client, request)
        except suds.WebFault as e:
            handle_response_exception(e, transaction)

        transaction.save()
        return transaction

    def auth_payment(self, payment):

        if not payment.completed():
            logger.error("Payment registration not completed")
            raise PaymentRegistrationNotCompleted(payment)

        client = get_client()
        operation = 'AUTH'

        request = get_netaxept_object(client, 'ProcessRequest')
        request.Operation = operation
        request.TransactionId = payment.transaction_id

        transaction = self.model(
            payment=payment,
            transaction_id=payment.transaction_id,
            operation=operation
        )
        try:
            response = process(client, request)
        except suds.WebFault as e:
            handle_response_exception(e, transaction)
        finally:
            transaction.save()

        return transaction

    def capture_payment(self, payment, amount):

        self.require_auth(payment)

        client = get_client()
        operation = 'CAPTURE'

        request = get_netaxept_object(client, 'ProcessRequest')
        request.Operation = operation
        request.TransactionId = payment.transaction_id
        request.TransactionAmount = amount

        transaction = self.model(
            payment=payment,
            transaction_id=payment.transaction_id,
            amount=amount,
            operation=operation
        )

        try:
            response = process(client, request)
        except suds.WebFault as e:
            handle_response_exception(e, transaction)
        finally:
            transaction.save()

        return transaction

    def credit_payment(self, payment, amount):

        self.require_auth(payment)

        if not self.get_query_set().filter(Q(operation='CAPTURE') | Q(operation='SALE'), payment=payment).exists():
            logger.error("No amount captured, cannot credit")
            raise NoAmountCaptured(payment, amount)

        client = get_client()
        operation = 'CREDIT'

        request = get_netaxept_object(client, 'ProcessRequest')
        request.Operation = operation
        request.TransactionId = payment.transaction_id
        request.TransactionAmount = amount

        transaction = self.model(
            payment=payment,
            transaction_id=payment.transaction_id,
            amount=amount,
            operation=operation
        )

        try:
            response = process(client, request)
        except suds.WebFault as e:
            handle_response_exception(e, transaction)
        finally:
            transaction.save()

        return transaction

    def annul_payment(self, payment):

        self.require_auth(payment)

        if self.get_query_set().filter(Q(operation='CAPTURE') | Q(operation='SALE'), payment=payment).exists():
            logger.error("Amount allready captured, cannot annul")
            raise AmountAllreadyCaptured(payment)

        client = get_client()
        operation = 'ANNUL'

        request = get_netaxept_object(client, 'ProcessRequest')
        request.Operation = operation
        request.TransactionId = payment.transaction_id

        transaction = self.model(
            payment=payment,
            transaction_id=payment.transaction_id,
            operation=operation
        )

        try:
            response = process(client, request)
        except suds.WebFault as e:
            logger.error("Annul on payment failed")
            handle_response_exception(e, transaction)
        finally:
            transaction.save()

        return transaction

    def require_auth(self, payment):
        if not self.get_query_set().filter(payment=payment, operation='AUTH').exists():
            logger.error("Payment not authorized")
            raise PaymentNotAuthorized(payment)
