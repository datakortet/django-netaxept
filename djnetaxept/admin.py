from datakortet.utils import kr_ore
from django.contrib import admin
from djnetaxept.models import NetaxeptPayment, NetaxeptTransaction


class NetaxeptPaymentOptions(admin.ModelAdmin):
    list_display = """
    id transaction_id Amount currencycode description ordernumber
    OK responsecode responsesource responsetext
    """.split()

    def Amount(self, pmt):
        return kr_ore(pmt.amount)
    Amount.allow_tags = True
    Amount.admin_order_field = 'amount'

    def OK(self, pmt):
        "Avoid having a double negative in the list_display."
        return not pmt.flagged
    OK.admin_order_field = 'flagged'
    OK.boolean = True


class NetaxeptTransactionOptions(admin.ModelAdmin):
    list_display = """
    id Payment transaction_id operation Amount OK
    responsecode responsesource responsetext
    """.split()
    raw_id_fields = ['payment']
    readonly_fields = ['Payment']

    def Payment(self, pmt):
        return u'<a href="/admin/djnetaxept/netaxeptpayment/%d/">%s</a>' % (
            pmt.payment_id, pmt.payment_id
        )
    Payment.allow_tags = True
    Payment.admin_order_field = 'payment'

    def Amount(self, pmt):
        return kr_ore(pmt.amount)
    Amount.allow_tags = True
    Amount.admin_order_field = 'amount'

    def OK(self, pmt):
        return not pmt.flagged
    OK.admin_order_field = 'flagged'
    OK.boolean = True

admin.site.register(NetaxeptPayment, NetaxeptPaymentOptions)
admin.site.register(NetaxeptTransaction, NetaxeptTransactionOptions)
