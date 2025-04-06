from collections import OrderedDict, defaultdict
from typing import List, Tuple

from accounts.models import Account
from currencies.models import Currency
from django.db.models import F, Q, Sum
from entries.models import Entry


class ChartAccDetails:
    def __init__(self, user, acc_id, period_from, period_to):
        self.user = user
        self.acc_id = int(acc_id)
        self.period_from = period_from
        self.period_to = period_to
        self.results = defaultdict(dict)
        self.period_sum: float = None
        self.total: float = None

    def aggregate(self):
        params = {
            'currency': Currency.objects.get(user=self.user, selected=True),
            'user': self.user,
            'date__gte': self.period_from,
            'date__lt': self.period_to,
        }
        acc = Account.objects.get(id=self.acc_id)
        group_field = 'acc_cr__name' if acc.acc_type == 'active' else 'acc_dr__name'
        group_id = 'acc_cr__id' if acc.acc_type == 'active' else 'acc_dr__id'
        self.results = (
            Entry.objects
            .filter(
                Q(acc_dr__parent_id=self.acc_id) | Q(acc_cr__parent_id=self.acc_id),
                **params,
            )
            .annotate(acc_name=F(group_field), acc_id=F(group_id))
            .values('acc_name', 'acc_id')
            .annotate(total_sum=Sum('total'))
        )
        self.total = sum(entr['total_sum'] for entr in self.results)


class ChartDataAggregator:
    def __init__(self, user, currency, period_from, period_to, group_by_parent, group_all):
        self.user = user
        self.currency = currency
        self.period_from = period_from
        self.period_to = period_to
        self.group_by_parent: bool = group_by_parent
        self.group_all: bool = group_all
        self.results = defaultdict(dict)
        self.inc_accounts = List[Tuple[int, str]]
        self.exp_accounts = List[Tuple[int, str]]
        self.period_inc: float = None
        self.period_exp: float = None
        self.period_sum: float = None

    def _create_querysets(self):
        qs_exp = (
            Entry.objects.filter(
                date__gte=self.period_from,
                date__lte=self.period_to,
                user=self.user,
                acc_dr__results=Account.RESULT_EXPENSES,
                currency=self.currency,
            )
            .select_related("acc_dr", "acc_dr__parent")
            .order_by("-acc_dr__parent__order")
        )
        qs_inc = (
            Entry.objects.filter(
                date__gte=self.period_from,
                date__lte=self.period_to,
                user=self.user,
                acc_cr__results=Account.RESULT_INCOMES,
                currency=self.currency,
            )
            .select_related("acc_cr", "acc_cr__parent")
            .order_by("-acc_cr__order")
        )
        return qs_inc, qs_exp

    def _get_period_results(self):
        incomes_sum = (
            Entry.objects.filter(
                date__gte=self.period_from,
                date__lte=self.period_to,
                user=self.user,
                acc_cr__results=Account.RESULT_INCOMES,
                currency=self.currency,
            )
            .values("total")
            .aggregate(sum=Sum("total"))["sum"]
            or 0
        )
        expenses_sum = (
            Entry.objects.filter(
                date__gte=self.period_from,
                date__lte=self.period_to,
                user=self.user,
                acc_dr__results=Account.RESULT_EXPENSES,
                currency=self.currency,
            )
            .values("total")
            .aggregate(sum=Sum("total"))["sum"]
            or 0
        )
        inc_sum = round(incomes_sum, 3)
        exp_sum = round(expenses_sum, 3)
        res_sum = round(incomes_sum - expenses_sum, 3)
        return inc_sum, exp_sum, res_sum

    def _create_group_string(self, entr, group_all):
        if group_all:
            return "Total"
        month = entr.date.strftime("%m")
        return f"{entr.date.year}.{month}"

    def _create_acc_name(self, entr, group_by_parent):
        if entr.acc_dr.results == Account.RESULT_EXPENSES:
            if group_by_parent:
                acc_name = (entr.acc_dr.parent.id, entr.acc_dr.parent.name) if entr.acc_dr.parent else (entr.acc_dr.id, entr.acc_dr.name)
            else:
                acc_name = f"{entr.acc_dr.parent.name}:{entr.acc_dr.name}" if entr.acc_dr.parent else f"{entr.acc_dr.name}"
        else:
            acc_name = (entr.acc_cr.id, entr.acc_cr.name)
        return str(acc_name)

    def _summarize_results(self, type_name, entries):
        for entr in entries:
            group_date = self._create_group_string(entr, self.group_all)
            acc_name = self._create_acc_name(entr, self.group_by_parent)
            if group_dict := self.results.get(group_date, {}).get(type_name):
                group_dict[acc_name] = group_dict.get(acc_name, 0) + entr.total
            else:
                new_value = OrderedDict()
                new_value[acc_name] = entr.total
                self.results[group_date][type_name] = new_value

    def _get_income_accounts(self, qs_inc):
        return {
            (acc['acc_cr__id'], acc['acc_cr__name'])
            for acc in qs_inc.values('acc_cr__id', 'acc_cr__name')
        }

    def _get_expenses_accounts(self):
        return (
            [
                (acc['id'], acc["name"])
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, parent=None, user=self.user).order_by("order").values('id', 'name')
            ]
            if self.group_by_parent
            else [
                (acc['id'], f'{acc["parent__name"]}:{acc["name"]}')
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, user=self.user).values("name", "parent__name").distinct()
            ]
        )

    def _get_max_value(self, results):
        max_inc = 0
        max_exp = 0
        for item in results.values():
            max_inc = max(sum(value for key, value in item.get("incs", {}).items()), max_inc)
            max_exp = max(sum(value for key, value in item.get("exps", {}).items()), max_exp)
        return max(max_inc, max_exp)

    def aggregate(self):
        qs_inc, qs_exp = self._create_querysets()
        self._summarize_results("exps", qs_exp)
        self._summarize_results("incs", qs_inc)
        self.inc_accounts = self._get_income_accounts(qs_inc)
        self.exp_accounts = self._get_expenses_accounts()
        self.period_inc, self.period_exp, self.period_sum = self._get_period_results()

    def dict(self):
        return {
            "max_value": self._get_max_value(self.results),
            "accounts_incomes": self.inc_accounts,
            "accounts_expenses": self.exp_accounts,
            "results": dict(sorted(self.results.items())),
            "period_inc": f'{self.period_inc:.3f}',
            "period_exp": f'{self.period_exp:.3f}',
            "period_sum": f'{self.period_sum:.3f}',
        }
