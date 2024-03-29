from currencies.models import Currency
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Account(models.Model):
    TYPE_ACTIVE = "a"
    TYPE_PASSIVE = "p"
    RESULT_ASSETS = "ast"
    RESULT_INCOMES = "inc"
    RESULT_EXPENSES = "exp"
    RESULT_DEBTS = "dbt"
    RESULT_PLANS = "pln"
    ACC_TYPES = (
        (TYPE_ACTIVE, _("active")),
        (TYPE_PASSIVE, _("passive")),
    )
    RESULT_TYPES = (
        (RESULT_ASSETS, _("assets")),
        (RESULT_INCOMES, _("incomes")),
        (RESULT_EXPENSES, _("expenses")),
        (RESULT_DEBTS, _("debts")),
        (RESULT_PLANS, _("planning")),
    )
    name = models.CharField(max_length=255)
    order = models.IntegerField(blank=True, default=0)
    parent = models.ForeignKey("self", related_name="child", on_delete=models.CASCADE, null=True, blank=True)
    acc_type = models.CharField(max_length=1, choices=ACC_TYPES, default=TYPE_ACTIVE)
    results = models.CharField(max_length=3, choices=RESULT_TYPES, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.name


class AccountBalance(models.Model):
    acc = models.ForeignKey(Account, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=15, decimal_places=3, default=0.0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.acc}: {self.total}"
