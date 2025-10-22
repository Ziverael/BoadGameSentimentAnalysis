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


from src.dynamic_scraper import Scraper
@dataclass
class Game():
    title : str
    players : str
    release : int
    tags : list
    age : str
    time : str
    category : str
    publisher : str
    description : str
    weight : float

    @staticmethod
    def extract_params(params_list) -> tuple:
        """
        Extract valid values from scraped paragraph with parameters
        """
        player = params_list[0][0]
        time = params_list[1][0]
        age = params_list[2][1]
        weight = float(params_list[3][2])
        return player, time, age, weight

    @staticmethod
    def get_title_and_release_date(scraper : Scraper) -> tuple:
        """
        Get title and release date from website.
        ARGS
        ----
        scraper [Scraper]   Scraper with proper URL address settled
        
        RETURN
        ------
        tuple of strings containing release date and title in the given order.

        """
        #Verify if the address is proper
        #TO DO
        #Get game title and release date
        title = scraper.scrape('div', class_ = "game-header-title-info", get_text = False)[1]
        title = scraper.scrape('h1', parent = title, get_text = True, all_results = False)
        title = re.sub( r'\t+', '' , title)
        #Get release date and cleare additional symbols
        release = re.findall(r"\(.+\)", title)[0]
        release = re.sub(r"[\(\)]", "", release)
        #Remove release date from
        title = re.sub(r" +\(\d+\) +", "", title)
        #Remove trailing spaces
        title = re.sub(r"^ +", "", title)
        return release, title

    @staticmethod
    def get_descriptions(scraper : Scraper) -> tuple:
        """
        Get short desription and longer paragraph
        ARGS
        ----
        scraper [Scraper]   Scraper with proper URL address settled
        
        RETURN
        ------
        tuple of strings containing short descroption and the longer one in the given order.
        """
        #Get short description
        short_desc = scraper.scrape('div', class_ = "game-header-title-container", get_text = False)[1]
        short_desc = scraper.scrape('p', parent = short_desc, all_results = False)
        #Remove trailing spaces and tabulations
        short_desc = re.sub(r'[\t ]+$', '', short_desc)
        # print(short_desc.get_text())
        # print(">>>", type(short_desc))
        # print(short_desc.find('p').get_text())
        # print(short_desc.findChildren('p')[0].get_text())
        # print(scraper.scrape("p", parent = short_desc, class_ = "ng-binding ng-scope"))
        # print(scraper.scrape("p", parent = short_desc))
        # print(scraper.scrape('p', parent = short_desc))
        # short_desc = scraper.scrape(
            # 'p',
            # parent = scraper.scrape('div', class_ = "game-header-title-info", get_text = False)[1]
        # )
        # print(short_desc)

