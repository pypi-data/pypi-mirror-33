import re


def between(start, end, text):
    result = re.search(r'' + start + '(.*?)' + end, text)
    if result:
        return result.group(1)
    else:
        return None


def after(start, text):
    result = re.search("(?:" + start + ")(.*)", text)
    if result:
        return result.group(1)
    else:
        return None
