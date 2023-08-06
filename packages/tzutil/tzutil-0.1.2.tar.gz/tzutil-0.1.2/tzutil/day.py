import re
# from reddit_hot import epoch_seconds
from datetime import timedelta, datetime

RE_NUM = re.compile("\d+")
DATE_BEGIN = datetime(1970, 1, 1)


def day_today():
    today = datetime.today()
    return (today - DATE_BEGIN).days


def day_from_epoch(year, month, day):
    """从1970.01.01到给定日期的天数"""
    date_time = datetime(year, month, day)
    return (date_time - DATE_BEGIN).days


def str2day(time_str):
    if time_str.isdigit():
        if len(time_str) == 8:
            args = (time_str[:4], time_str[4:6], time_str[6:])
    else:
        args = RE_NUM.findall(time_str)[:3]
    return day_from_epoch(*map(int, args))


def datetime_from_day(day):
    """从1970.01.01的天数到datetime对象"""
    beg_date_time = datetime(1970, 1, 1)
    return beg_date_time + timedelta(days=day)


def day2str(day):
    return str(datetime_from_day(day))[:10]

# def str2time(time_str, time_zone=8 * 3600):
#     return epoch_seconds(
#         datetime(*map(int, RE_NUM.findall(time_str)))
#     ) - time_zone


from datetime import date


def weekday(day=None):
    if day is None:
        day = day_today()
    return (day + 3) % 7 + 1


def workday_lastest(day=None):
    if day is None:
        day = day_today()
    week = weekday(day)
    diff = week - 5
    if diff < 0:
        diff = 0
    return day - diff


if __name__ == "__main__":
    print(day2str(str2day("20160909")))
