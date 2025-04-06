from datetime import datetime


def parse_dates(period):
    period_from = datetime.strptime(period, "%Y.%m")
    if period_from.month == 12:
        period_to = period_from.replace(year=period_from.year + 1, month=1, day=1)
    else:
        period_to = period_from.replace(month=period_from.month + 1, day=1)

    return period_from, period_to
