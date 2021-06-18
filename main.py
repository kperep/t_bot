# -*- coding: cp1251 -*-
import const
import requests
import telebot
import datetime
import json
from kinopoisk_api import KP

bot = telebot.TeleBot(const.telegram_token)


# ������� ��� ��������� ������ �� ���������
def get_address_from_coords(coords):
    PARAMS = {
        "apikey": "11f65570-477c-49f6-b8f6-b138ace5388a",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }
    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        if coords[0].isalpha():
            ans = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            return "���� ����������: " + ans
        else:
            address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
            return "���� �����: " + address_str
    except Exception as e:
        # ���� �� ������, �� ���������� ������
        return "��������� ������!"


def log_and_print(user, user_id, message, chat_id):
    with open(str(user_id) + '.log', 'a') as f:
        f.write('{0} ({1})  -  {2}\n'.format(user_id, user, str(datetime.datetime.now())))
        f.write('-----------------------------------------------------------\n')
        f.write(message + '\n')
        if user == 'Bot':
            bot.send_message(chat_id, message)
        f.write('-----------------------------------------------------------\n')


def main():
    @bot.message_handler(commands=['help', 'start'])
    def send_welcome(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        log_and_print('Bot', message.from_user.id, '������! � Telegram-��� ��� ��������� �������� ����������.\n��� '
                                                   '�������:\n/help - ������� ������ ��������� ������\n/location - '
                                                   '���������� ����� �� �����������\n/currency - ��������� ������\n/film '
                                                   '- ������ ������� ������ �� ���������� � IMDb\n/weather - �������� '
                                                   '������ �� �������� ������', message.chat.id)

    @bot.message_handler(commands=['film'])
    def send_welcome(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        log_and_print('Bot', message.from_user.id, '������� �������� ������:', message.chat.id)
        bot.register_next_step_handler(message, film)

    def film(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        kinopoisk = KP(token=const.kinopoisk_token)
        search = kinopoisk.search(message.text)
        if len(search) == 0:
            log_and_print('Bot', message.from_user.id, '�� ������ ������� ������ �� �������.', message.chat.id)
            return
        log_and_print('Bot', message.from_user.id, str(search[0].ru_name) + ' ' + str(search[0].year) + ' ����\n������� �� ����������: ' + str(search[0].kp_rate), message.chat.id)

    @bot.message_handler(commands=['currency'])
    def send_welcome(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        log_and_print('Bot', message.from_user.id, '������� ������ �� ������� ���������� (��������, USD, RUB):',
                      message.chat.id)
        bot.register_next_step_handler(message, f_currency)

    def f_currency(message):
        global from_currency
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        from_currency = message.text
        log_and_print('Bot', message.from_user.id, '������� ���������� ������:', message.chat.id)
        bot.register_next_step_handler(message, am)

    def am(message):
        global amount
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        amount = message.text
        log_and_print('Bot', message.from_user.id, '������� ������ � ������� ����������:', message.chat.id)
        bot.register_next_step_handler(message, t_currency)

    def t_currency(message):
        global to_currency
        global amount
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        to_currency = message.text
        currency = requests.get(const.currency_url).json().get("rates")
        if from_currency.upper() not in currency or to_currency.upper() not in currency:
            log_and_print('Bot', message.from_user.id, '����������� ������!', message.chat.id)
            return
        if not amount.isdigit():
            log_and_print('Bot', message.from_user.id, '������������ ���������� ������!', message.chat.id)
            return
        amount = float(amount)
        f_amount = amount
        if from_currency != "USD":
            amount = amount / currency.get(from_currency.upper())
        result = round(amount * currency.get(to_currency.upper()), 2)
        log_and_print('Bot', message.from_user.id,
                      str(f_amount) + ' ' + from_currency.upper() + ' ����� ' + str(result) + ' ' + to_currency.upper(),
                      message.chat.id)

    @bot.message_handler(commands=['location'])
    def send_welcome(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        log_and_print('Bot', message.from_user.id, '������� ��� ���������� (��������, "37.617585, 55.751903"):\n� '
                                                   '���� �� ������ ���� ���������� - ������� ��� ���� ����� � � �����'
                                                   ' ���� ����������!',
                      message.chat.id)
        bot.register_next_step_handler(message, location)

    def location(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        coords = message.text
        address_str = get_address_from_coords(coords)
        log_and_print('Bot', message.from_user.id, address_str, message.chat.id)

    @bot.message_handler(commands=['weather'])
    def send_welcome(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        log_and_print('Bot', message.from_user.id, '������ � ����� ������ �� ������ ������?', message.chat.id)
        bot.register_next_step_handler(message, weather)

    def weather(message):
        log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
        url = const.weather_url.format(message.text, const.weather_token)
        response = requests.get(url)
        if response.status_code != 200:
            log_and_print('Bot', message.from_user.id, '����� �� ������!', message.chat.id)
            return
        data = json.loads(response.content)
        for elem in data['weather']:
            weather_state = elem['main']
        temp = round(data['main']['temp'] - 273.15, 2)
        city = data['name']
        msg = f'The weather in {city}: Temp is {temp}, State is {weather_state}'
        log_and_print('Bot', message.from_user.id, msg, message.chat.id)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        if "������" in message.text.lower():
            log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
            log_and_print('Bot', message.from_user.id, "������, ��� � ���� ���� ������?", message.chat.id)
        else:
            log_and_print(message.from_user.username, message.from_user.id, message.text, message.chat.id)
            log_and_print('Bot', message.from_user.id, "� ���� �� �������. ������ /help.", message.chat.id)

    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
