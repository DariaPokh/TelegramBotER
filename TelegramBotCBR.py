from datetime import datetime
import xml.etree.ElementTree as et
import requests
import telebot

TOKEN = "***"

bot = telebot.TeleBot(TOKEN)


def parse_data(date):
    url = 'https://www.cbr.ru/scripts/XML_daily.asp'
    params = {
        'date_req': date
    }

    response = requests.get(url, params)
    tree = et.ElementTree(et.fromstring(response.text))
    root = tree.getroot()
    values_str = ""
    for node in root:
        s_nominal = node.find("Nominal").text if node is not None else None
        s_name = node.find("Name").text if node is not None else None
        s_value = node.find("Value").text if node is not None else None

        values_str += f"{s_nominal} {s_name} - {s_value} руб.\n\n"
    return values_str


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Приветствую!\n\n" +
        "Добро пожаловать в справочник курса валют. " +
        "В справочнике доступны курсы валют с сайта ЦБ РФ с 01.01.2000." +
        "\n\nНа какую дату Вас интересует курс валют? Введите в формате ДД.ММ.ГГГГ."
    )


@bot.message_handler(content_types=["text"])
def handle_text(message):
    selected_date = "".join(message.text.split())
    try:
        valid_date = datetime.strptime(selected_date, "%d.%m.%Y")
        if valid_date >= datetime.now():
            bot.send_message(message.chat.id,
                             "Курс валют доступен до сегодняшнего дня включительно. Попробуйте еще раз.")

            @bot.message_handler(content_types=["text"])
            def text(new_massage):
                return handle_text(new_massage)

        elif valid_date < datetime.strptime("01.01.2000", "%d.%m.%Y"):
            bot.send_message(message.chat.id, "Курс валют доступен с 01.01.2000 г. Попробуйте еще раз.")

            @bot.message_handler(content_types=["text"])
            def text(new_massage):
                return handle_text(new_massage)
        else:
            bot.send_message(message.chat.id, parse_data(selected_date))

    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат ввода даты. "
                                          "Попробуйте еще раз. "
                                          "Введите в формате ДД.ММ.ГГГГ.")

        @bot.message_handler(content_types=["text"])
        def text(new_massage):
            return handle_text(new_massage)


bot.polling(none_stop=True)
