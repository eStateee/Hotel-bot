import requests
import json
from decouple import config
from loguru import logger

KEY = config('KEY')


def highprice_hotels(city_id, user):
    """
         1) current  = цена
         2) name = Название
         3) starRating = Рейтинг
         4) streetAddress = адрес(АНГЛ)
         5) label = 'City center', distance = Расстояние от центра(Есть еще другие значения label, УКАЗЫВАТЬ city Center ОБЯЗ)
         6) rating = рейтинг гостей
       """

    # CONSTANTS,

    CURRENCY_TUPLE = ('USD', 'RUB')
    MAX_HOTELS = '25'
    CURRENCY = 'RUB'  # По умолчанию, будет изменем пользователем, и проверен в CURRENCY_TUPLE

    # USER DATA

    if user.currency not in CURRENCY_TUPLE:
        user.currency = CURRENCY

    if int(user.hotels) >= int(MAX_HOTELS):
        user.hotels = MAX_HOTELS

    # TO FILL

    adres = 'Not found'
    name = 'Not found'
    star_rating = 0
    guest_rating = 'Not found'
    price = 'Not found'
    dist_from_center = 'Not found'  # in miles

    # Поиск нужных ключей
    def find_el(tree, element_name):
        if element_name in tree:
            return tree[element_name]
        for key, sub_tree in tree.items():
            if isinstance(sub_tree, dict):
                result = find_el(tree=sub_tree, element_name=element_name)
                if result:
                    break
        else:
            result = None
        return result

    #################################################################################################################

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": city_id, "pageSize": user.hotels, "sortOrder": "PRICE_HIGHEST_FIRST",
                   "locale": "en_US",
                   "currency": user.currency}

    headers = {
        'x-rapidapi-key': KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    #################################################################################################################
    try:
        for _ in find_el(data, 'results'):
            pass
    except TypeError:
        yield False
        return False

    res = find_el(data, 'results')  # получение словаря со всеми данными
    for i in res:
        adres = find_el(i, 'streetAddress')

        name = find_el(i, 'name')

        guest_rating = find_el(i, 'rating')

        star_rating = find_el(i, 'starRating')

        dist_from_center = str(round(float(find_el(i, 'landmarks')[0]['distance'].split(' ')[0]) * 1.6, 2)) + ' Km'

        price = find_el(i, 'current')

        yield f'<b>Adress</b>: {adres}\n<b>Name</b>: {name}\n<b>Guest rate</b>: {guest_rating}\n<b>Star rate</b>: {star_rating}\n<b>Distance from center</b>: ' \
              f'{dist_from_center}\n<b>Price</b>: {price}'
