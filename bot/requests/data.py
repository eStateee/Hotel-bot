import requests
import json
from decouple import config
from loguru import logger

KEY = config('KEY')


def city_idd(city_country):
    # CONSTANTS
    CITY = city_country.split(',')[0].lower()
    COUNTRY = city_country.split(',')[1].lower()

    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": city_country, "locale": "en_US"}

    headers = {
        'x-rapidapi-key': KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        all_cities = data['suggestions'][0]['entities']
    except Exception:
        logger.error('API response error')
        return False


    city_id = 0
    for i in all_cities:
        if i['name'].lower() == CITY:
            city_id = i['destinationId']
            break
    return city_id
