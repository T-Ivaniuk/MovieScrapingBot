from configfile_utilits import *
from gv_api import gv_parser
from tp_api import theprojector_parser
from telebot import types
from telebot import TeleBot
from telebot import custom_filters
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import os
import smtplib
import datetime
import time

files_dir = folder_for_tg
cinema_types = ["[TP]", "[GV]"]
bot = TeleBot(telegramtoken)  # parse_mode=None #
bot.add_custom_filter(custom_filters.ChatFilter())


def timestamp_now():
    """just a timestamp in seconds"""
    return int(time.time())


def human_time_now_up_to_minute():
    """timestamp in readable (for humans) format"""
    date_time = datetime.datetime.fromtimestamp(time.time())
    return date_time.strftime("%Y-%m-%d_%H-%M")


def day(number):
    """formatted date in specific day"""
    return (datetime.date.today() + datetime.timedelta(days=number)).strftime("%a, %d %b %Y")


def validate(string):
    """
    returns True if telegram message is a movie scraping request
    returns False if not
    """
    try:
        datetime.datetime.strptime(string[5:], "%a, %d %b %Y")
        return string[:4] in cinema_types
    except:
        return False


def day_diff(d2):
    """difference between to dates (up to day)"""
    d1 = datetime.date.today().day
    d2 = datetime.datetime.strptime(d2, "%a, %d %b %Y").day

    return d2 - d1


def create_folder():
    """little func to create folder for files if not exist"""
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)


def bot_started_alert():
    """send message to all whitelist tg users - bot alive"""
    for key in telegramwhitelist.keys():
        try:
            print(key, telegramwhitelist[key])
            bot.send_message(key, f"GVBot started \nyour mail: {telegramwhitelist[key]}", reply_markup=main_markup())
        except:
            pass


def main_markup():
    """
    main menu telegeram keyboard
    :return: markup
    """
    markup = types.ReplyKeyboardMarkup()
    test_button = types.KeyboardButton('Test')
    getID_button = types.KeyboardButton('GetID')
    tp_button = types.KeyboardButton("Theprojector")
    gv_button = types.KeyboardButton("Golden Village")
    markup.row(test_button, getID_button)
    markup.row(tp_button, gv_button)

    return markup


def gv_markup():
    """
    telegram GoldenVillage (GV) cinema keyboard
    :return: markup
    """
    markup = types.ReplyKeyboardMarkup()

    button_0 = types.KeyboardButton("[GV] " + day(0))
    button_1 = types.KeyboardButton("[GV] " + day(1))
    button_2 = types.KeyboardButton("[GV] " + day(2))
    button_3 = types.KeyboardButton("[GV] " + day(3))
    button_4 = types.KeyboardButton("[GV] " + day(4))
    button_5 = types.KeyboardButton("[GV] " + day(5))
    button_6 = types.KeyboardButton("[GV] " + day(6))
    button_back = types.KeyboardButton("Back")
    markup.row(button_0)
    markup.row(button_1, button_2, button_3)
    markup.row(button_4, button_5, button_6)
    markup.row(button_back)

    return markup


def tp_markup():
    """
    telegram theprojector (TP) cinema keyboard
    :return: markup
    """
    markup = types.ReplyKeyboardMarkup()
    button_0 = types.KeyboardButton("[TP] " + day(0))
    button_1 = types.KeyboardButton("[TP] " + day(1))
    button_2 = types.KeyboardButton("[TP] " + day(2))
    button_3 = types.KeyboardButton("[TP] " + day(3))
    button_4 = types.KeyboardButton("[TP] " + day(4))
    button_5 = types.KeyboardButton("[TP] " + day(5))
    button_6 = types.KeyboardButton("[TP] " + day(6))
    button_back = types.KeyboardButton("Back")
    markup.row(button_0)
    markup.row(button_1, button_2, button_3)
    markup.row(button_4, button_5, button_6)
    markup.row(button_back)

    return markup


def listener(messages):
    """func to catch and print sent messages to the console """
    for m in messages:
        if m.content_type == 'text':
            print("username: " + str(m.chat.first_name),
                  " | whitelist_pass: " + str(m.chat.id in telegramwhitelist),
                  " | user_id:", str(m.from_user.id) +
                  " | chat_id: " + str(m.chat.id) +
                  " | message:", m.text)


def get_all_mails():
    """returns list of all email addresses in whitelist"""
    mail_list = []
    for mail in telegramwhitelist.values():
        mail_list.append(mail)
    return mail_list


def send_file_via_tg(file_name: str, chat_id: int):
    """
    :param file_name:str file name to open and send via tg
    :param chat_id:int
    :return:
    """
    doc = open(file_name, 'rb')
    bot.send_document(chat_id, doc)
    print(f"message was sent successfully to {chat_id}")


def send_email(file_to_send: str, receiver: list, filename: str):
    """
    just awesome send email func
    file name and list of receiver(s) are required to make some magic
    :param file_to_send: filename to open and attach to message
    :param receiver: list of whitelist mails to receive message
    :param filename: attachment name
    :return:
    """
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gmail_sender, gmail_password)
        msg = MIMEMultipart()
        msg.attach(MIMEText(filename))
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_to_send, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)
        print(f'receiver: {receiver}')
        msg['From'] = gmail_sender
        msg['To'] = ", ".join(receiver)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "ad-hoc report"
        server.sendmail(gmail_sender, receiver, msg.as_string())
        server.quit()
        return f"message was sent successfully to {receiver} \n"
    except Exception as E:
        return f"mail send error: \n{E}"


@bot.message_handler(chat_id=telegramwhitelist, func=lambda message: message.text == "Test")
def send_welcome(message):
    """just test button (whitelist required)"""
    bot.reply_to(message, "Howdy, how are you doing?", reply_markup=main_markup())


@bot.message_handler(func=lambda message: message.text == "GetID")
def command_text_getid(message):
    """returns telegram profile id (whitelist NOT required)"""
    bot.reply_to(message, message.chat.id, reply_markup=main_markup())


@bot.message_handler(chat_id=telegramwhitelist, func=lambda message: message.text == "Theprojector")
def send_welcome(message):
    """Theprojector scraping menu (whitelist required)"""
    bot.reply_to(message, message.text, reply_markup=tp_markup())


@bot.message_handler(chat_id=telegramwhitelist, func=lambda message: message.text == "Golden Village")
def send_welcome(message):
    """GoldenVillage scraping menu (whitelist required)"""
    bot.reply_to(message, message.text, reply_markup=gv_markup())


@bot.message_handler(chat_id=telegramwhitelist, func=lambda message: message.text == "Back")
def send_welcome(message):
    """back to main menu button (whitelist required)"""
    bot.reply_to(message, "mainpage", reply_markup=main_markup())


@bot.message_handler(chat_id=telegramwhitelist, func=lambda message: validate(string=message.text))
def scraping_func(message):
    """
    allows scrape TG or GV cinema via telegram menu
    :param message:
    :return:
    """
    create_folder()
    bot.send_message(message.chat.id, message.text)
    filename = f"{message.text[1:3].lower()}-{human_time_now_up_to_minute()}.xlsx"
    if message.text[:4] == "[TP]":
        file_to_send = theprojector_parser(filename=files_dir + filename, day=day_diff(message.text[5:]))
    elif message.text[:4] == "[GV]":
        file_to_send = gv_parser(filename=files_dir + filename, day=day_diff(message.text[5:]))

    send_email_resp = send_email(file_to_send, [telegramwhitelist[message.chat.id]], filename=filename)
    bot.reply_to(message, send_email_resp)
    send_file_via_tg(chat_id=message.chat.id, file_name=file_to_send)


def infitiy_polling():
    while True:
        try:
            bot.polling(non_stop=True, timeout=33)
        except Exception as e:
            print(e)
            time.sleep(5)


bot_started_alert()
print("telegram bot started")
bot.set_update_listener(listener)

infitiy_polling()
