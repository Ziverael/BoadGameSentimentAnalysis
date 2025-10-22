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

class JSONLWriter():
    def __init__(self, output_):
        self.output = output_
    
    def overwrite(self, input_):
        """Write to file. If flie already exists, then overwrite it."""
        with open(self.output, 'w') as f:
            writer = jsonlines.Writer(f)
            if isinstance(input_, dict):
                writer.write(input_)
            elif isinstance(input_, list):
                for line in input_:
                    writer.write(line)
            else:
                raise Exception("Expected dictionary or list of dictionaries.")


    def write(self, input_):
        """Write to file. If flie already exists, then append content."""
        with open(self.output, 'a') as f:
            writer = jsonlines.Writer(f)
            if isinstance(input_, dict):
                writer.write(input_)
            elif isinstance(input_, list):
                for line in input_:
                    writer.write(line)
            else:
                raise Exception("Expected dictionary or list of dictionaries.")
