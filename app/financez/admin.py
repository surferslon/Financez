from django.contrib import admin

from .models import Account, AccountBalance, Currency, Entry

admin.site.register(Entry)
admin.site.register(Account)
admin.site.register(Currency)
admin.site.register(AccountBalance)
