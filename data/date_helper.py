from datetime import datetime,date


def date_now(ftime: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.now().strftime(ftime)


def day_now(ftime: str = '%Y-%m-%d'):
    return date.today().strftime(ftime)


def month_now():
    return day_now('%m')


def year_now():

    return day_now('%Y')


def time_now():
    return date_now('%H:%M:%S')