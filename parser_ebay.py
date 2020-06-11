import requests
from bs4 import BeautifulSoup
import csv
# from multiprocessing import Pool
# from math import copysign
# import concurrent.futures
from threading import Thread
import warnings
import os
import pandas as pd
from datetime import datetime


class Parser:
    def __init__(self):
        self.val = 0
        self.search = ''
        self.urls = []
        self.output = [] # List of numebrs of urls for workers
        self.content = []
        self.run()

    def make_urls(self) -> None:
        for num in range(1, self.val + 1):
            self.urls.append(f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={self.search}&_sacat=0&_pgn={num}')
        return
    
    def for_workers(self) -> None: # Makes a list of numbers which workers should parse
        num = 0
        for i in range(1, self.val+1):
            if i == self.val:
                self.output.append(self.val)
                break 
            if num == 10:
                if len(self.output) == 0:
                    self.output.append(num)
                else:
                    self.output.append(num * len(self.output))
                num = 0
            num += 1
        if len(self.output) == 1:
            pass
        else:
            self.output = self.output[1:len(self.output)]
        return
    
    def write(self):
        count = 1
        with open(f'{self.search.replace("+", " ")}.csv', 'a+', encoding="utf-8") as file:
            pen = csv.writer(file)
            pen.writerow(('Count', 'Name', 'Price', 'Link'))
            for i in self.content:
                pen.writerow([int(count), i['title'].strip(), i['price'].strip(), i['link'].strip()])
                count += 1

        # Creating xlsx from csv
        file = pd.read_csv(f'{self.search.replace("+", " ")}.csv')
        file.to_excel(f'{self.search.replace("+", " ")}.xlsx', index=None, header=True)

        # Deleting csv file
        os.remove(f'{self.search.replace("+", " ")}.csv')

    def main(self, start, end) -> None:
        for i in range(start, end):
            r = requests.get(self.urls[i])
            soup = BeautifulSoup(r.text, 'lxml')
            li = soup.find_all('div', attrs={'class': 's-item__info clearfix'})
            for i in li:
                title = i.find('h3', attrs={'class': 's-item__title'}).text
                a = i.find('a', attrs={'class': 's-item__link'}).get('href')
                price = i.find('span', attrs={'class': 's-item__price'}).text
                self.content.append(({'title': title,
                                 'price': price,
                                 'link': a}))

            return

    def question(self):
        self.search = input('Type what to search\n>> ').strip()
        self.search = self.search.replace(' ', '+')
        self.val = input("Type how many pages do you want to parse\n>> ").strip()
        try:
            self.val = int(self.val)
            return
        except ValueError:
            warnings.warn('You entered wrong word!!')
            self.question()

    def run(self):
        self.question()
        self.make_urls()
        self.for_workers()
        start = 0
        end = self.output[0]
        now = datetime.now()
        threads = []
        for i in range(1, len(self.output)+1):
            t = Thread(target=self.main, args=(start, end), daemon=True)
            t.start()
            threads.append(t)
            start = end
            if i == len(self.output):
                break
            else:    
                end = self.output[i]
        for t in threads:
            t.join(10.0)
            t.is_alive()
        self.write()
        print(datetime.now() - now)


if __name__ == '__main__':
    parser = Parser()
