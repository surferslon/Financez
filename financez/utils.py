from .models import Account


def add_subaccounts(acc_list, filtered_list):
    result_tree = []
    for acc in filtered_list:
        parent_id = acc['id']
        subaccounts = list(filter(lambda x: x['parent_id'] == parent_id, acc_list))
        if subaccounts:
            acc['subaccs'] = subaccounts
            for subacc in subaccounts:
                subacc['subaccs'] = add_subaccounts(
                    acc_list,
                    filter(lambda x: x['parent_id'] == subacc['id'], acc_list)
                )
        result_tree.append(acc)
    return result_tree


def make_account_tree():
    accounts = Account.objects.all().values('id', 'parent_id', 'name', 'order').order_by('order')
    acc_list = [acc for acc in accounts]
    return add_subaccounts(acc_list, filter(lambda x: x['parent_id'] is None, acc_list))
