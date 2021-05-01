import heapq
import os
import psycopg2
import requests
import dj_database_url
from bs4 import BeautifulSoup

from bot import bot
from data_generator import Top_of_country

DATABASE_URL = os.environ['DATABASE_URL']

db_info = dj_database_url.config(default=DATABASE_URL)

conn = psycopg2.connect(database=db_info.get('NAME'),
                        user=db_info.get('USER'),
                        password=db_info.get('PASSWORD'),
                        host=db_info.get('HOST'),
                        port=db_info.get('PORT'))

cursor = conn.cursor()

cursor.execute('''CREATE TABLE USERNAMES(
                 ID SERIAL PRIMARY KEY,
                 USERNAME VARCHAR(255) NOT NULL);''')
conn.commit()


def get_countries_list():
    url = 'https://www.noxinfluencer.com/instagram-channel-rank/top-100-ru-all-sorted-by-followers-weekly'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    areas = soup.find(attrs={"id": "area-filter-select"})
    area_ids = areas.find_all("option",
                              {"class": "check-agree area-filter-item"})
    return list(filter(lambda country: country != "all",
                       map(lambda area_id: area_id.get("value"), area_ids)))


def merge_tops():
    countries = get_countries_list()
    generators = map(lambda country:
                     Top_of_country(country=country).get_next_top(), countries)

    for profile in heapq.merge(*generators, key=(lambda p: p[1]), reverse=True):
        print(f'{profile[0]}')
        yield profile


def main():
    parsed = 0
    for profile in merge_tops():
        parsed += 1
        with conn.cursor() as cursor:
            cursor.execute(f'INSERT INTO USERNAMES (USERNAME)'
                           f'VALUES (\'{profile[0]}\');')
            conn.commit()
        print(f'Add user {parsed}: {profile[0]} '
              f'({profile[1]} followers.)')

        if parsed == 5000:
            break

    bot.polling(none_stop=True, interval=0)


if __name__ == "__main__":
    main()
