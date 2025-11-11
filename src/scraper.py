import sys

import requests
from bs4 import BeautifulSoup as bsp


class SimpleScraper:
    def __init__(self, page):
        self.__page = page
        self.__page_response = None
        self.__isScraped = False
        self.__soup = None
        self._set_soup_()

    @property
    def page(self):
        return self.__page

    @property
    def soup(self):
        return self.__soup

    def _set_soup_(self):
        """Try to connect to get response from web page and store data to atributes."""
        if not self.__isScraped:
            self.__isScraped = True
            try:
                self.__page_response = requests.get(self.__page)
            except Exception as e:
                print(f"Error during connection try: {e}", file=sys.stderr)
                raise e
            self.__soup = bsp(self.__page_response.content, "html.parser")

    def set_page(self, page):
        """Set page's URL and get its source and prepare soup."""
        self.__isScraped = False
        self.__page = page
        self._set_soup_()

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
