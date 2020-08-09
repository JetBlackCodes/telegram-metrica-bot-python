import telebot
import config
import requests
import json

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

YM_API_URL = "https://api-metrika.yandex.ru/stat/v1/data"


@bot.message_handler(commands=['start'])
def welcome(message):
    sticker = open('static/welcome.tgs', 'rb')
    bot.send_sticker(message.chat.id, sticker)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Операционные системы АО")
    item2 = types.KeyboardButton("Браузеры АО")
    markup.add(item1, item2)

    if message.chat.type == "private":
        bot.send_message(message.chat.id,
                         "Не думал, что ты зайдешь, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот для показа "
                         "Яндекс Метрики проекта старое-ЭДО за последний месяц".format(
                             message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)

    else:
        bot.send_message(message.chat.id,
                         "Ого сколько вас тут! {0.first_name} спасибо что пригласил на тусу!\n"
                         "Я - <b>{1.first_name}</b>, бот для показа "
                         "Яндекс Метрики проекта старое-ЭДО за последний месяц".format(
                             message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main(message):
    if message.text == "Браузеры АО" or message.text == "Операционные системы АО":

        if message.text == "Браузеры АО":
            metrics = ['ym:s:visits', 'ym:s:users']
            dimensions = ['ym:s:browserAndVersionMajor']
            title = "<b>Версия браузера: Посещения - Юзеры</b>\n"

        elif message.text == "Операционные системы АО":
            metrics = ['ym:s:visits', 'ym:s:users']
            dimensions = ['ym:s:operatingSystem']
            title = "<b>Версия ОС: Посещения - Юзеры</b>\n"

        metrics_string = ','.join(metrics)
        dimensions_string = ','.join(dimensions)

        params = {
            'date1': '30daysAgo',  # startDate
            'date2': 'today',  # endDate
            'id': config.counterIdAO,
            'dimensions': dimensions_string,
            'metrics': metrics_string,
            'oauth_token': config.TOKEN
        }

        res = requests.get(YM_API_URL, params=params)
        data = json.loads(res.text)
        result_data = data['data']

        array = [title]

        for i in result_data:
            name = i['dimensions'][0]['name']
            my_metrics = i['metrics']
            visits = my_metrics[0]
            users = my_metrics[1]
            stroka = "<b>{0}:</b> {1} - {2}".format(name, str(int(visits)), str(int(users)))
            array.append(stroka)

        result = "\n".join(array)

        if len(result) > 4096:
            for x in range(0, len(str(array)), 4096):
                bot.send_message(message.chat.id, result[x:x + 4096], parse_mode='html')
        else:
            bot.send_message(message.chat.id, result, parse_mode='html')

    # inline keyboard example

    # markup = types.InlineKeyboardMarkup(row_width=2)
    # item1 = types.InlineKeyboardButton("Кайф", callback_data='good')
    # item2 = types.InlineKeyboardButton("Ну такое", callback_data='bad')
    # markup.add(item1, item2)

    else:
        bot.send_message(message.chat.id, 'Я не могу знать всего, но смысл жизни точно - 42')


# inline keyboards callback example

# @bot.callback_query_handler(func=lambda call:True)
# def callback_inline(call):
#     try:
#         if call.message:
#             if call.data == 'good':
#                 bot.send_message(call.message.chat.id, 'По кайфу')
#             elif call.data == 'bad'
#                 bot.send_message(call.message.chat.id, 'Бывает...')
#
#             #remove inline buttons
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Браузеры", reply_markup=None)
#
#             #show alert
#             bot.answer_callback_query(chat_id=call.message.chat.id, show_alert=False, text="Это текстовое уведомление!!!")
#
#     except Exception as e:
#         print(repr(e))


# RUN
bot.polling(none_stop=True)
