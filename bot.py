import psycopg2
import telebot
import dj_database_url
import os


DATABASE_URL = os.environ['DATABASE_URL']

db_info = dj_database_url.config(default=DATABASE_URL)

bot = telebot.TeleBot('1757542734:AAF2DqXowSHFn7vnG0tuaUleHbOCzwBf6aM')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                 'Я InstaBot, привет! Напиши мне любое слово, и я найду его среди юзернеймов самых популярных людей в instagram!')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    word = message.text.lower()
    conn = psycopg2.connect(database=db_info.get('NAME'),
                            user=db_info.get('USER'),
                            password=db_info.get('PASSWORD'),
                            host=db_info.get('HOST'),
                            port=db_info.get('PORT'))
    res = []
    with conn.cursor() as cursor:
        query_params = (f'%{word.strip()}%',)
        cursor.execute(
            'SELECT USERNAME FROM USERNAMES WHERE USERNAME LIKE %s;', query_params)
        for row in cursor:
            res.append(row[0])
        conn.commit()
        conn.close()
    if not res:
        bot.send_message(message.from_user.id, 'К сожалению, совпадений нет.')
    else:
        bot.send_message(message.from_user.id, f'Вот что я нашел:')
        while res:
            result = ''
            while res and len(result + '\n' + res[0]) < 4096:
                result += "\n"
                result += res[0]
                del res[0]
            bot.send_message(message.from_user.id, result)


if __name__ == '__main__':
   pass

