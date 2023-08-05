from datetime import datetime


def now():
    return datetime.now()


def delta(start, end):
    return end - start
