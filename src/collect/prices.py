import re

from bs4.element import Tag
from pydantic import BaseModel

from src.dynamic_scraper import Scraper


class Price(BaseModel):
    value: float
    currency: str


def get_prices(scraper: Scraper, game_page_url: str) -> list[Price]:
    scraper.set_page(game_page_url)
    shopping_sections = scraper.scrape(
        "section", class_="shopping-listing-module", get_text=False
    )
    market_section = get_market_section(shopping_sections)
    prices_tags_text = [x.find("a").text for x in market_section.find_all("li")]
    return list(map(extract_price, prices_tags_text))


def get_market_section(elements: list[Tag]) -> Tag:
    for section in elements:
        if "GeekMarket" in section.find("h3").text:
            return section
    msg = "Missing GeekMarket section."
    raise RuntimeError(msg)


def extract_price(raw_text: str):
    text = " ".join(raw_text.split())
    match = re.search(r"([€$£])\s?(\d+(?:\.\d{2})?)", text)
    if match:
        currency, price = match.groups()
    return Price(value=price, currency=currency)


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    link = "https://boardgamegeek.com/boardgame/357873/the-old-kings-crown"
    scraper = Scraper(link, timeout=10, proxy=None)
    logger.info(get_prices(scraper, link))
