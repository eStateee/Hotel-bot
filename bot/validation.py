import re


# TODO
#  1) сделать проверку ввода
#  2) начать разбираться с логгингом, админкой


def city_check(user):
    pattern = r'\b[a-zA-Z]{0,10},[a-zA-Z]{0,10}'
    user = user.replace(' ', '')

    try:
        res = re.findall(pattern, user)
        if res[0] == user:
            return True
    except Exception:
        return False


def min_max_price_check(user):
    pattern = r'\b\d{0,10} \d{0,10}\b'

    try:
        res = re.findall(pattern, user)
        if res[0] == user:
            return True
        return False
    except Exception:
        return False


def distance_check(user):
    pattern = r'\b\d{0,10}\b'

    try:
        res = re.findall(pattern, user)
        if res[0] == user:
            return True
        return False
    except Exception:
        return False


def hotels(user):
    pattern = r'\b\d{0,10}\b'

    try:
        res = re.findall(pattern, user)
        if res[0] == user:
            return True
        return False
    except Exception:
        return False
