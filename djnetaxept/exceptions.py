# -*- coding: utf-8 -*-


class BaseNetaxeptException(Exception):
    """Base class for Netaxept exceptions.
    """
    def __init__(self, *args, **kwargs):
        super(BaseNetaxeptException, self).__init__(
            *(args or (self.__class__.__doc__,)),
            **kwargs
        )


class PaymentNotAuthorized(BaseNetaxeptException):
    """Payment not authorized
    """


class AmountAllreadyCaptured(BaseNetaxeptException):
    """Amount allready captured, do a CREDIT
    """


class NoAmountCaptured(BaseNetaxeptException):
    """No amount captured nothing to CREDIT
    """


class PaymentRegistrationNotCompleted(BaseNetaxeptException):
    """Payment registration is not completed yet
    """
    

class ProcessException(Exception):
    pass
