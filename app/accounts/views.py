from django.shortcuts import render
from financez.models import Account
from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class AccountListView(ListAPIView):
    def add_subaccounts(self, acc_list, filtered_list):
        result_tree = []
        for acc in filtered_list:
            parent_id = acc["pk"]
            if subaccounts := list(filter(lambda x: x["parent_id"] == parent_id, acc_list)):
                acc["subaccs"] = subaccounts
                for subacc in subaccounts:
                    subacc["subaccs"] = self.add_subaccounts(
                        acc_list, filter(lambda x: x["parent_id"] == subacc["pk"], acc_list)
                    )
            result_tree.append(acc)
        return result_tree

    def make_account_tree(self, user, section=None):
        if section:
            accounts = (
                Account.objects.filter(results=section, user=user)
                .values("pk", "parent_id", "name", "order", "acc_type", "results")
                .order_by("order")
            )
        else:
            accounts = (
                Account.objects.filter(user=user)
                .values("pk", "parent_id", "name", "order", "results")
                .order_by("order")
            )
        acc_list = list(accounts)
        return self.add_subaccounts(acc_list, filter(lambda x: x["parent_id"] is None, acc_list))

    def get(self, request):
        # whats a crap
        user = request.user
        account_list = self.make_account_tree(user)
        categorized_dict = {
            "assets": [acc for acc in account_list if acc["results"] == "ast"],
            "expenses": [acc for acc in account_list if acc["results"] == "exp"],
            "plans": [acc for acc in account_list if acc["results"] == "pln"],
            "incomes": [acc for acc in account_list if acc["results"] == "inc"],
            "debts": [acc for acc in account_list if acc["results"] == "dbt"],
        }
        return Response(categorized_dict)
