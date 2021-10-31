import telebot
from decouple import config
from bot.requests.data import city_idd
from bot.requests.lowprice import lowprice_hotels
from bot.requests.highprice import highprice_hotels
from bot.requests.bestdeal import bestdeal_hotels
from bot.validation import city_check, distance_check, min_max_price_check, hotels
import time
from bot.models import *
from loguru import logger

# Connect database
with db:
    db.create_tables([Request])
TOKEN = config('TOKEN')

bot = telebot.TeleBot(TOKEN)

COMMANDS = ['/lowprice', '/highprice', '/bestdeal']

low_flag = False
high_flag = False
best_flag = False

# Configure Logger
logger.add('bot/log/logg.log', format="{time} {level} {message}",
           level="DEBUG",
           rotation='5MB', compression='zip', encoding='utf-8')
logger.info("Start Logging")


class User:
    def __init__(self):
        self.hotels = ''
        self.city_country = ''
        self.distance = 0
        self.min_price = ''
        self.max_price = ''
        self.currency = ''


user = User()


# Welcome letter
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     "Hello! {0.first_name}, That's the hotel guide from company Too Easy Travel".format(
                         message.from_user))

    bot.send_message(message.chat.id, 'To learn the Rules and Help write\n<b> /rules </b>\n<b> /help </b>',
                     parse_mode='html')


# help commands
@bot.message_handler(commands=['rules'])
def rules(message):
    bot.send_message(message.chat.id,
                     '1) Please write ALL the commands/text in English(moscow Voronesh, New york Sydney)'
                     '\n2) Follow the commands description and writing sequence',
                     parse_mode='html')


@bot.message_handler(commands=['help'])
def help(message):
    """
    /lowprice - the lowest hotel price
    /highprice - the highest hotel price
    /bestdeal - the best hotel by price and CENTER
    /help - gives a help console
    """
    bot.send_message(message.chat.id,
                     'Choose the interesting command below:\n'
                     '<b> /help </b> - Help\n'
                     '<b> /lowprice </b> - Cheap hotels\n'
                     '<b> /highprice </b> - Expensive hotels\n'
                     '<b> /bestdeal </b> - Best deal hotels'
                     'Distance - km'
                     '', parse_mode='html')


@bot.message_handler(commands=['highprice'])
def highprice(message):
    global high_flag
    high_flag = True
    msg = bot.send_message(message.chat.id, 'Enter City and Country im format:  <b>City, Country</b>',
                           parse_mode='html')
    bot.register_next_step_handler(msg, city)


@bot.message_handler(commands=['lowprice'])
def lowprice(message):
    global low_flag
    low_flag = True
    msg = bot.send_message(message.chat.id, 'Enter City and Country im format:  <b>City, Country</b>',
                           parse_mode='html')
    bot.register_next_step_handler(msg, city)


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    global best_flag
    best_flag = True
    msg = bot.send_message(message.chat.id, 'Enter City and Country im format:  <b>City, Country</b>',
                           parse_mode='html')
    bot.register_next_step_handler(msg, city)


def city(message):
    user.city_country = message.text
    if not city_check(user.city_country):
        logger.error(
            f'{message.from_user.first_name}-{message.from_user.id} called "city" with WRONG params: '
            f'{user.city_country}')
        msg = bot.send_message(message.chat.id, ' Error!!  Enter City and Country im format: <b>City, Country</b>',
                               parse_mode='html')
        bot.register_next_step_handler(msg, city)
    else:

        msg = bot.send_message(message.chat.id, 'Enter currency (<b>RUB, USD</b>) default - <b>RUB</b>', parse_mode='html')
        bot.register_next_step_handler(msg, currency)


def max_hotels(message):
    user.hotels = message.text
    if not hotels(user.hotels):
        logger.error(
            f'{message.from_user.first_name}-{message.from_user.id} called "max_hotels" with WRONG params: '
            f'{user.hotels}')
        msg = bot.send_message(message.chat.id, ' Error!!  Enter max hotels quantity ')
        bot.register_next_step_handler(msg, max_hotels)
    else:
        bot.send_message(message.chat.id, 'Searching for hotels, please wait...')
        response(message)


def distance(message):
    user.distance = message.text
    if not distance_check(user.distance):
        logger.error(
            f'{message.from_user.first_name}-{message.from_user.id} called "distance" with WRONG params: '
            f'{user.distance}')
        msg = bot.send_message(message.chat.id, ' Error!!  Enter max ditance from center(km) ')
        bot.register_next_step_handler(msg, distance)
    else:

        msg = bot.send_message(message.chat.id, 'Enter <b>max quantity</b> of hotels to search for ',parse_mode='html')
        bot.register_next_step_handler(msg, max_hotels)


def price(message):
    pricee = message.text
    if not min_max_price_check(pricee):
        msg = bot.send_message(message.chat.id, 'Error enter price again in format: <b>min_price max_price </b>',
                               parse_mode='html')
        bot.register_next_step_handler(msg, price)
    else:
        pricee = pricee.split(' ')

        user.min_price = pricee[0]

        user.max_price = pricee[1]
        logger.info(
            f'{message.from_user.first_name}-{message.from_user.id} called "price"  params: {user.min_price},'
            f'{user.max_price}')
        msg = bot.send_message(message.chat.id, 'Enter <b>max distance</b> from City Center(km)', parse_mode='html')
        bot.register_next_step_handler(msg, distance)


def currency(message):
    user.currency = message.text.upper()
    if not best_flag:

        msg = bot.send_message(message.chat.id, 'Enter <b>max quantity</b> of hotels to search for ',parse_mode='html')
        bot.register_next_step_handler(msg, max_hotels)
    else:
        msg = bot.send_message(message.chat.id, 'Enter price again in format: <b>min_price max_price </b>',
                               parse_mode='html')
        bot.register_next_step_handler(msg, price)


@bot.message_handler(commands=['history'])
def history(message):
    count = 1
    with db:
        all_history = Request.select().where(Request.user_id == message.from_user.id)

        for i in all_history:
            if count > 10:
                break

            print(count)
            count += 1
            bot.send_message(message.chat.id,
                             f'<b>Тип запроса</b>: {i.type}\n\n<b>Отели</b>:\n{i.hotels}\n<b>Время запроса</b>: '
                             f'{i.date}',
                             parse_mode='html')


def response(message):
    hotel_id = city_idd(user.city_country)

    if low_flag:
        full_info = lowprice_hotels(hotel_id, user)
        output(message, full_info)

    elif high_flag:
        full_info = highprice_hotels(hotel_id, user)
        output(message, full_info)

    elif best_flag:
        full_info = bestdeal_hotels(hotel_id, user)
        output(message, full_info)


def output(message, full_info):
    for i_hotel in full_info:
        if i_hotel == False:
            bot.send_message(message.chat.id, 'Ooooops smth went wrong, please try again')
            break
        time.sleep(1)
        bot.send_message(message.chat.id, i_hotel, parse_mode='html')
    if hotels == '':
        hotels = 'Error, Hotels not found'
    with db:
        Request(type=type, user_id=message.from_user.id, hotels=hotels, date=datetime.datetime.now()).save()


    global low_flag, best_flag, high_flag
    low_flag, best_flag, high_flag = False, False, False


# Valid request check
@bot.message_handler(content_types=['text'])
def check_message(message):
    if message.text not in COMMANDS:
        bot.send_message(message.from_user.id, "I don't know such command(")


# RUN
bot.polling(none_stop=True)
