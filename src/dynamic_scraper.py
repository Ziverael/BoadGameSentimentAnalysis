import sys

from bs4 import BeautifulSoup as bsp
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait

from src.scraper import SimpleScraper


class Scraper(SimpleScraper):
    """Scraper class using Selenium during scraping. It allows wait for loading dynamic js content."""

    def __init__(self, page, timeout, proxy=None):
        options = ChromeOptions()
        options.add_argument("--headless=new")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        self.__driver = webdriver.Chrome(
            options=options,
        )
        self.__page = page
        self.__page_response = None
        self.__isScraped = False
        self.__soup = None
        self.__timeout = timeout
        self.__proxy = proxy
        self._set_soup_()

    @property
    def page(self):
        return self.__page

    @property
    def timeout(self):
        return self.__timeout

    @property
    def proxy(self):
        return self.__proxy

    @property
    def soup(self):
        return self.__soup

    def _set_soup_(self):
        """
        Set soup, page response and driver. If __isScraped is True then ommit those actions.
        """
        if not self.__isScraped:
            self.__isScraped = True
            try:
                self.__driver.get(self.__page)
            except Exception as e:
                print(f"Error during connection try: {e}", file=sys.stderr)
                raise e
            self.__page_response = self.__driver.page_source
            self.__soup = bsp(self.__page_response, "html.parser")

    def set_page(self, page):
        """Set page's URL and get its source and prepare soup."""
        self.__isScraped = False
        self.__page = page
        self._set_soup_()

    def wait_for_elem(self, class_, verbose=False):
        """Wait for element with provided class name and then load page_src."""
        if verbose:
            print(f"Waiting for element {class_}...")
        WebDriverWait(self.__driver, timeout=self.__timeout).until(
            lambda x: x.find_element(By.CLASS_NAME, class_)
        )
        self.__page_response = self.__driver.page_source
        self.__soup = bsp(self.__page_response, "html.parser")

    def scrape(
        self, tag, class_=None, id_=None, all_results=True, parent=None, get_text=True
    ):
        """
        Scrape matching tags
        ARGS
        ----
        tag [str]   tag type
        class_  [str]   tag class
        all_results [bool]  return all results or first results
        parent [object]    if provided, then search only childs of given element
        get_text    [bool]  if True return text from tag. Otherwise return tag

        RETURN
        ------
        if all_results is True then return list of tags. Otherwise return single object.
        If attribute page_src is empty then return -1.
        """
        if not self.__isScraped:
            self._set_soup_()
        # Set function args
        if class_ and id_:
            args = [tag, {"class": class_, "id": id_}]
        elif class_:
            args = [tag, {"class": class_}]
        elif id_:
            args = [tag, {"id": id_}]
        else:
            args = [tag]
        # Scrape data
        if all_results:
            if parent:
                if get_text:
                    return [i.get_text() for i in parent.findChildren(*args)]
                return [i for i in parent.findChildren(*args)]
            if get_text:
                return [i.get_text() for i in self.__soup.find_all(*args)]
            return [i for i in self.__soup.find_all(*args)]

        if parent:
            if get_text:
                return parent.findChildren(*args)[0].get_text()
            return parent.findChildren(*args)[0]
        if get_text:
            return self.__soup.find(*args).get_text()
        return self.__soup.find(*args)

    def quit(self) -> None:
        self.__driver.close()
        self.__driver.quit()
