from datetime import datetime

from django.db.models import Sum

from .models import Account, Entry


def add_subaccounts(acc_list, filtered_list):
    result_tree = []
    for acc in filtered_list:
        parent_id = acc["pk"]
        subaccounts = list(filter(lambda x: x["parent_id"] == parent_id, acc_list))
        if subaccounts:
            acc["subaccs"] = subaccounts
            for subacc in subaccounts:
                subacc["subaccs"] = add_subaccounts(
                    acc_list, filter(lambda x: x["parent_id"] == subacc["pk"], acc_list)
                )
        result_tree.append(acc)
    return result_tree


def make_account_tree(user, section=None):
    if section:
        accounts = (
            Account.objects.filter(results=section, user=user)
            .values("pk", "parent_id", "name", "order", "acc_type", "results")
            .order_by("order")
        )
        acc_list = [acc for acc in accounts]
        return add_subaccounts(acc_list, filter(lambda x: x["parent_id"] is None, acc_list))
    else:
        accounts = (
            Account.objects.filter(user=user).values("pk", "parent_id", "name", "order", "results").order_by("order")
        )
        acc_list = [acc for acc in accounts]
        return add_subaccounts(acc_list, filter(lambda x: x["parent_id"] is None, acc_list))


def calculate_taxes(year, quarter=None):
    tax_rate = 6
    if quarter:
        q_mapping = {
            1: {"date__gte": datetime(year, 1, 1), "date__lt": datetime(year, 4, 1)},
            2: {"date__gte": datetime(year, 4, 1), "date__lt": datetime(year, 7, 1)},
            3: {"date__gte": datetime(year, 7, 1), "date__lt": datetime(year, 10, 1)},
            4: {
                "date__gte": datetime(year, 10, 1),
                "date__lt": datetime(year + 1, 1, 1),
            },
        }
        period = q_mapping.get(quarter)
    else:
        period = {
            "date__gte": datetime(year, 1, 1),
            "date__lt": datetime(year + 1, 1, 1),
        }

    result = {"income_usd": 0, "income_rub": 0, "tax": 0}
    for e in Entry.objects.filter(acc_dr=Account.objects.get(name="transit usd"), **period):
        print(e)
        _, rate = e.comment.split(" ")
        rate = float(rate.replace(",", "."))
        result["income_usd"] += e.total
        result["income_rub"] += e.total * rate
        result["tax"] += ((e.total * rate) * tax_rate) / 100

    print(result)


def get_current_balance(acc, currency):
    incomes = Entry.objects.filter(acc_dr=acc, currency=currency).aggregate(sum=Sum("total"))
    expenses = Entry.objects.filter(acc_cr=acc, currency=currency).aggregate(sum=Sum("total"))
    return (incomes["sum"] or 0) - (expenses["sum"] or 0)
