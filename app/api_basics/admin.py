from django.contrib import admin

from .models import TransactionV2, Wallet

# Register your models here.
admin.site.register(Wallet)
admin.site.register(TransactionV2)
