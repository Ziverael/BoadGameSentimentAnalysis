#!/usr/bin/python
###IMPORTS###
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions

from bs4 import BeautifulSoup as bsp
import os
import sys
import pandas as pd
import numpy as np
import requests #Communicatrion with web
from selenium import webdriver # Dynamic scraping for JS websites
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import re
import csv
from dotenv import load_dotenv
from sys import stderr
from dataclasses import dataclass, asdict
from src.scraper import SimpleScraper
from src.dynamic_scraper import Scraper
from src.model import Game
from typing import Final
        
BASE_URL: Final[str] = "https://boardgamegeek.com"
CATEGORIES_URL: Final[str] = f"{BASE_URL}/browse/boardgamecategory"
GAMES_URL: Final[str] = "https://boardgamegeek.com/browse/boardgame"
TIMEOUT: Final[int] =10
PROXY: Final[str | None] = None
GAMES_NO: int = 304

def get_games_pages(scraper: SimpleScraper, limit: int) -> list[str]:
    links: list[str] = []
    page_no: int = 0
    while len(links) < limit:
        page_no += 1
        pageURL = GAMES_URL + "/" + str(page_no)
        scraper.set_page(pageURL)
        links.extend(
            scraper.scrape(
                'a',
                class_ = "primary",
                get_text = False,
                parent = scraper.scrape(
                    'table',
                    id_ = "collectionitems",
                    get_text = False,
                    all_results = False,
                )
            )
        )
    return links[:limit]

###FUNCTIONS###
def main():
    links = get_games_pages(SimpleScraper(BASE_URL), GAMES_NO)
    print(len(links))
    raise ValueError("Yo!")
    #Load variables
    load_dotenv()
    #Set variables
    pages = 2
    LIMIT = 2
    iter = 0
    games_links = []

    #Initialize scraper

    #Get categories
    categories = reqScraper.scrape('a', parent = reqScraper.scrape('table', get_text = False, all_results = False))

    #Get games links
    for page_no in range(1, pages + 1):
        pageURL = gamesURL + "/" + str(page_no)
        reqScraper.set_page(pageURL)
        games_links.extend(
            reqScraper.scrape(
                'a',
                class_ = "primary",
                get_text = False,
                parent = reqScraper.scrape('table', id_ = "collectionitems", get_text = False, all_results = False)
            )
        )
    games_links = [ baseURL + link.get('href') for link in games_links]
    print(games_links)

    dynamic_scraper = Scraper(baseURL, timeout = TIMEOUT, proxy = PROXY)
    for idx, link in enumerate(games_links):
        print(f"Loop:{idx}")
        
        print(link)
        dynamic_scraper.set_page(link)
        
        #Get game parameters
        params = dynamic_scraper.scrape('p', class_ = "gameplay-item-primary", get_text = False)
        #Split paragraphs to single words
        params = [re.split(r'[\t ]+', par.get_text()) for par in params]
        #Remove empty elements
        params = [list(filter(lambda t: t != "", par)) for par in params]
        print(params)
        #Parse games parameters
        extracted_params = Game.extract_params(params)
        print(extracted_params)
        #Get release date and game title
        release, title = Game.get_title_and_release_date(dynamic_scraper)
        print(release, title)
        #Get description
        description = Game.get_descriptions(dynamic_scraper)

if __name__ == "__main__":
    main()
    iter = 0
    #Load variables
    load_dotenv()

    # baseURL = os.getenv("BASE_URL")
    # bggURL = "https://boardgamegeek.com/browse/boardgamecategory"
    # gamesURL = os.getenv("GAMES_URL")
    # shopURL = os.getenv("SHOP_URL")
    # pages = 2
    # LIMIT = 3
    # iter = 0

    # ###VARIABLES###
    # games = pd.DataFrame(
    #     {"title" : [],
    #     "release" : [],
    #     "tags" : [],
    #     "age" : [],
    #     "time" : [],
    #     "category" : [],
    #     "publisher" : [],
    #     "description" : [],
    #     "players" : [],
    #     'price_warehouse': [],
    #     'price_sell': [],
    #     'price_borrow': []
    #     }
    # )
    # fail = False
    # err =None
    # tags = set()
    # vals = [
    #     5,
    #     10,
    #     15,
    #     20,
    #     30,
    #     10000
    # ]


    # try: 
    #     cats = requests.get(bggURL)

    #     soup = bsp(cats.content, 'html.parser')
    #     print(type(cats), type(soup))
    #     categories = soup.find('table')
    #     categories = [cat_.get_text() for cat_ in categories.findAll('a')]
    #     # print(categories)
    #     # Get games links
    #     games_links = []
    #     for page_no in range(1, pages + 1):#Pass (1,10)
    #         gamesPage = requests.get(gamesURL + "/" + str(page_no))
    #         gamesSoup = bsp(gamesPage.content, 'html.parser')
    #         gamesPage = gamesSoup.find('table', id = "collectionitems")
    #         games_links.extend(gamesPage.find_all("a", {"class" : "primary"}))
    #     # Prepare links
    #     games_links = [ baseURL + link.get('href') for link in games_links]
    #     #Scrap games details
    #     # Warning. Those webpages are filled dynamicly so you have to do it different way
    #     options = Options()
    #     options.add_argument("--headless")
    #     driver = webdriver.Firefox(options = options) 
    # except:
    #     print("Problem during scraping games list")
    #     sys.exit(1)

    # for link in games_links:
    #     # Try connection for every single link
    #     try:
    #     #Get page
    #         print(link)
    #         driver.get(link)
    #         page = driver.page_source
    #         page = bsp(page, 'html.parser')
    #         # Get game parameters
    #         params = page.find_all('div', {"class" : 'gameplay-item-primary'})
    #         params = [re.split( r'[\t ]+', par.get_text()) for par in params]
    #         params = [list(filter(lambda t: t != "", par)) for par in params]
    #         players = params[0][0]
    #         time = params[1][0]
    #         age = params[2][1]
    #         # Get title 
    #         title = page.find_all('div', {"class" : "game-header-title-container"})[1]
    #         title = title.findChildren('div', {"class" : "game-header-title-info"})[0]
    #         title = re.sub( r'\t+', '' , title.findChildren('a')[0].get_text())
    #         #  Get release date
    #         release = re.sub( r'[\t()]+', '', page.find('span', {"class" : "game-year"}).get_text())
    #         # Get short description
    #         desc = page.find_all('div', {"class" : "game-header-title-container"})[1]
    #         # desc = re.sub( r'\W+', '', desc.find('p').get_text()) 
    #         desc = re.sub( r'\t+', '', desc.find('p').get_text()) 
    #         #Get tags and categoty
    #         details1 = [
    #             re.sub( r'\W+', '', feat.get_text())
    #             for feat in 
    #             page.find_all('div', {'class': 'feature-title'})[:2]
    #             ]
    #         cat_, tags_ = [
    #             re.findall(
    #                 '[A-Z][^A-Z]*',
    #                 re.sub( r'\W+', '', feat.get_text())
    #             )
    #             for feat in 
    #             page.find_all('div', {'class': 'feature-description'})[:2]
    #             ]
            
    #         for val in  ('N', 'A', "Viewpollandresults"):
    #             if val in cat_:
    #                 cat_.remove(val)
    #             if val in tags_:
    #                 tags_.remove(val)
    #         tags_[-1] = re.sub('[0-9]+more', '', tags_[-1])
    #         # Get publisher [TO FIX]
    #         publisher = page.find_all('div', {"class", "game-header-credits"})[1]
    #         if len(publisher.findChildren('li')) == 3:
    #             publisher = publisher.findChildren('li')[2]
    #         else:
    #             publisher = publisher.findChildren('li')[1]
    #         publisher = publisher.findChildren('a')[0].get_text()
    #         #Insert data to dictionary
    #         game = {
    #             "title" : title,
    #             "release" : release,
    #             "tags" : "###".join(tags_), 
    #             "age" : age,
    #             "time" : time,
    #             "category" : cat_[0],
    #             "publisher" : publisher,
    #             "description" : desc,
    #             "players" : players
    #         }
    #         # print(game)

    #         #Wyłuskanie ceny
    #         try:
    #             driver.get("https://www.google.com/search?q=" +
    #                 title +
    #                 "+gra+planszowa+ceneo"
    #             "Gry_planszowe;szukaj-" + title)
    #             page = driver.page_source
    #             page = bsp(page, 'html.parser')
    #             page = page.find('div', {"id" : 'res'})
    #             page = page.find('a', href = True)  
    #             print(page["href"])
    #             # Move to offers
    #             driver.get(page["href"])
    #             page = driver.page_source
    #             page = bsp(page, 'html.parser')
    #             prices = page.find_all('div', {"class" : "product-offer__product__price"})
    #             prices = [price.find('span', {"class" : "price"}).get_text() for price in prices]
    #             prices = [*map(lambda t: float(re.sub(',', '.', t)), prices)]
    #             prices.sort()
    #             # print(prices)
    #             if not len(prices):
    #                 med = 100000
    #                 sd = 0
    #             elif len(prices) % 2:
    #                 med = prices[len(prices) // 2]
    #                 sd = np.std(prices)
    #             else:
    #                 med = (prices[len(prices) // 2] + prices[len(prices) // 2 - 1]) / 2
    #                 sd = np.std(prices)
    #         except:
    #             #If error occurs during loadin website or the website does not exist put None
    #             med = 100000
    #             sd = 0
    #         conds = [
    #             med < 40.00,
    #             med < 80.00,
    #             med < 120.00,
    #             med < 180.00,
    #             med < 250.00,
    #             med >= 250.00
    #         ]
    #         # Add prices to dict
    #         game["price_warehouse"] = med if med != 100000 else None
    #         game["price_sell"] = med + 0.5 * sd if med != 100000 else None
    #         borrow_price = int(np.select(conds, vals))
    #         game["price_borrow"] = borrow_price if borrow_price != 10000 else None
    #         # Update data frames
    #         games.loc[len(games)] = game
    #         # games = games.append(game, ignore_index = True) Depreciated
    #         tags.update(tags_)
    #         iter += 1
    #         if iter >= LIMIT:
    #             break
    #     except Exception as e:
    #         print("Connection error for {}\nError message:{}".format(link, e))

    #         # Czy turniejowa: round((players > 1) * random.random())

    #         # Terminy zwrotów generujemy jako data pobrania + czas między 1-6dni, aby zwrot nastąpił w godzinach pracy skleu

    # driver.close()
    # driver.quit()
    # # Save scraped data to csv file despite the connection status
    # games.to_csv('games.csv', index = False)
    # with open('tags.csv', 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(tags)

    # # Raise exception if connection failed
    # # ---------