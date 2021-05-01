import requests
from bs4 import BeautifulSoup
import time


class Top_of_country():
    def __init__(self, country):
        self.country = country
        self.generator = self.get_next_top()

    def get_next_top(self):
        page = 1
        print(f'Load {self.country} users page {page}...')
        while page <= 5:
            time.sleep(2)
            self.url = f'https://www.noxinfluencer.com/instagram-channel-rank/_influencer-rank?country={self.country}&category=all&rankSize=250&type=4&interval=weekly&order=followers&pageNum='
            response = requests.get(self.url + str(page))
            while response.status_code != 200:
                print(f'Code {response.status_code}. Waiting for retry...')
                time.sleep(int(response.headers['Retry-After']))
                print('Retry..')
                response = requests.get(self.url + str(page))
            print('Success!')
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.find_all('tr', class_='item')
            profiles = []
            for item in items:
                tag = item.find('a')
                username = tag.get('href').split('/')[-1]
                followers_items = item.find_all(attrs={
                    'class': 'text followerNum with-num',
                })
                followers_rank = followers_items[1].get_text()
                followers = followers_rank.strip().split(' ')[0]
                if 'K' in followers or 'M' in followers:
                    if followers[-1] == 'K':
                        followers = float(followers[:-1]) * 1000
                    elif followers[-1] == 'M':
                        followers = float(followers[:-1]) * 1000000
                    else:
                        followers = float(followers)
                profiles.append((username, int(followers)))
            if not profiles:
                break
            n = 0
            while n < len(profiles):
                yield profiles[n]
                n += 1
            page += 1
