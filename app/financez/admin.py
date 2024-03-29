from accounts.models import Account, AccountBalance
from currencies.models import Currency
from django.contrib import admin
from entries.models import Entry

admin.site.register(Entry)
admin.site.register(Account)
admin.site.register(Currency)
admin.site.register(AccountBalance)
