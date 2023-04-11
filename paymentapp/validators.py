import datetime


def is_month_year_in_past(month, year):
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    if year < current_year:
        return True
    elif year == current_year:
        if month < current_month:
            return True

    return False
