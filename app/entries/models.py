from accounts.models import Account, AccountBalance
from currencies.models import Currency
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext as _


def update_balance(acc, currency):
    balance, new = AccountBalance.objects.get_or_create(acc=acc, currency=currency)
    incomes = Entry.objects.filter(acc_dr=acc, currency=currency).aggregate(sum=Sum("total"))
    expenses = Entry.objects.filter(acc_cr=acc, currency=currency).aggregate(sum=Sum("total"))
    balance.total = (incomes["sum"] or 0) - (expenses["sum"] or 0)
    balance.save()


class Entry(models.Model):
    date = models.DateField()
    acc_dr = models.ForeignKey(Account, related_name="acc_dr", on_delete=models.CASCADE)
    acc_cr = models.ForeignKey(Account, related_name="acc_cr", on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=15, decimal_places=3, default=0.0)
    comment = models.CharField(max_length=1024, default="", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")

    def __str__(self):
        return f"{self.date} {self.acc_dr} {self.acc_cr} {self.total}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        update_balance(self.acc_dr, self.currency)
        update_balance(self.acc_cr, self.currency)
