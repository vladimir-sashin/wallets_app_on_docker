from django.contrib import admin

from .models import TransactionReport, TransactionV2, Wallet

# Register your models here.
admin.site.register(Wallet)
admin.site.register(TransactionV2)
admin.site.register(TransactionReport)
