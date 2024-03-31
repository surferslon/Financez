from collections import OrderedDict, defaultdict

from accounts.models import Account
from django.db.models import Sum
from entries.models import Entry


class ChartDataAggregator:
    def __init__(self, user, currency, period_from, period_to, group_by_parent, group_all):
        qs_inc, qs_exp = self._create_querysets(period_from, period_to, user, currency)
        self.results = defaultdict(dict)
        self._summarize_results(self.results, "exps", qs_exp, group_by_parent, group_all)
        self._summarize_results(self.results, "incs", qs_inc, group_by_parent, group_all)
        self.inc_accounts = self._get_income_accounts(qs_inc)
        self.exp_accounts = self._get_expenses_accounts(user, group_by_parent)
        self.period_inc, self.period_exp, self.period_sum = self._get_period_results(period_from, period_to, user, currency)

    def _create_querysets(self, period_from, period_to, user, currency):
        qs_exp = (
            Entry.objects.filter(
                date__gte=period_from,
                date__lte=period_to,
                user=user,
                acc_dr__results=Account.RESULT_EXPENSES,
                currency=currency,
            )
            .select_related("acc_dr", "acc_dr__parent")
            .order_by("-acc_dr__parent__order")
        )
        qs_inc = (
            Entry.objects.filter(
                date__gte=period_from,
                date__lte=period_to,
                user=user,
                acc_cr__results=Account.RESULT_INCOMES,
                currency=currency,
            )
            .select_related("acc_cr", "acc_cr__parent")
            .order_by("-acc_cr__order")
        )
        return qs_inc, qs_exp

    def _get_period_results(self, date_from, date_to, user, currency):
        incomes_sum = (
            Entry.objects.filter(
                date__gte=date_from,
                date__lte=date_to,
                user=user,
                acc_cr__results=Account.RESULT_INCOMES,
                currency=currency,
            )
            .values("total")
            .aggregate(sum=Sum("total"))["sum"]
            or 0
        )
        expenses_sum = (
            Entry.objects.filter(
                date__gte=date_from,
                date__lte=date_to,
                user=user,
                acc_dr__results=Account.RESULT_EXPENSES,
                currency=currency,
            )
            .values("total")
            .aggregate(sum=Sum("total"))["sum"]
            or 0
        )
        inc_sum = round(incomes_sum, 3)
        exp_sum = round(expenses_sum, 3)
        res_sum = round(incomes_sum - expenses_sum, 3)
        return f"{inc_sum:.3f}", f"{exp_sum:.3f}", f"{res_sum:.3f}"

    def _create_group_string(self, entr, group_all):
        if group_all:
            return "Total"
        month = entr.date.strftime("%m")
        return f"{entr.date.year}.{month}"

    def _create_acc_name(self, entr, group_by_parent):
        if entr.acc_dr.results == Account.RESULT_EXPENSES:
            if group_by_parent:
                acc_name = f"{entr.acc_dr.parent.name}" if entr.acc_dr.parent else f"{entr.acc_dr.name}"
            else:
                acc_name = f"{entr.acc_dr.parent.name}:{entr.acc_dr.name}" if entr.acc_dr.parent else f"{entr.acc_dr.name}"
        else:
            acc_name = f"{entr.acc_cr.name}"
        return acc_name

    def _summarize_results(self, results, type_name, entries, group_by_parent, group_all):
        for entr in entries:
            group_date = self._create_group_string(entr, group_all)
            acc_name = self._create_acc_name(entr, group_by_parent)
            if group_dict := results.get(group_date, {}).get(type_name):
                group_dict[acc_name] = group_dict.get(acc_name, 0) + entr.total
            else:
                new_value = OrderedDict()
                new_value[acc_name] = entr.total
                results[group_date][type_name] = new_value

    def _get_income_accounts(self, qs_inc):
        return [f"{acc}" for acc in set(qs_inc.values_list("acc_cr__name", flat=True))]

    def _get_expenses_accounts(self, user, group_by_parent):
        return (
            [
                f'{acc["name"]}'
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, parent=None, user=user).order_by("order").values("name")
            ]
            if group_by_parent
            else [
                f'{acc["parent__name"]}:{acc["name"]}'
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, user=user).values("name", "parent__name").distinct()
            ]
        )

    def _get_max_value(self, results):
        max_inc = 0
        max_exp = 0
        for item in results.values():
            max_inc = max(sum(value for key, value in item.get("incs", {}).items()), max_inc)
            max_exp = max(sum(value for key, value in item.get("exps", {}).items()), max_exp)
        return max(max_inc, max_exp)

    def dict(self):
        return {
            "max_value": self._get_max_value(self.results),
            "accounts_incomes": self.inc_accounts,
            "accounts_expenses": self.exp_accounts,
            "results": self.results,
            "period_inc": self.period_inc,
            "period_exp": self.period_exp,
            "period_sum": self.period_sum,
        }
