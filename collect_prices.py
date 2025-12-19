import json
from typing import Final

from pydantic import BaseModel
from tqdm import tqdm

from src.collect.details import (
    get_title_and_release_date,
)
from src.collect.prices import Price, get_prices
from src.dynamic_scraper import Scraper
from src.scraper import SimpleScraper


BASE_URL: Final[str] = "https://boardgamegeek.com"
CATEGORIES_URL: Final[str] = f"{BASE_URL}/browse/boardgamecategory"
GAMES_URL: Final[str] = "https://boardgamegeek.com/browse/boardgame"
TIMEOUT: Final[int] = 10
PROXY: Final[str | None] = None
GAMES_NO: int = 200


class GamePrice(BaseModel):
    title: str
    prices: list[Price]


def get_games_pages(scraper: SimpleScraper, limit: int) -> list[str]:
    links: list[str] = []
    page_no: int = 0
    while len(links) < limit:
        page_no += 1
        pageURL = GAMES_URL + "/" + str(page_no)
        scraper.set_page(pageURL)
        links.extend(
            scraper.scrape(
                "a",
                class_="primary",
                get_text=False,
                parent=scraper.scrape(
                    "table",
                    id_="collectionitems",
                    get_text=False,
                    all_results=False,
                ),
            )
        )
    links = [BASE_URL + a.get("href") for a in links[:limit]]
    return links[:limit]


class PartialResultsError(Exception):
    """Raised when data collection fails but partial results are available."""

    def __init__(self, message: str, results: list, cause: Exception | None = None):
        super().__init__(message)
        self.results = results
        self.__cause__ = cause


def collect_games_price(scraper: Scraper, links: list[str]):
    games_data: list[GamePrice] = []
    try:
        for link in tqdm(links):
            scraper.set_page(link)
            title, _ = get_title_and_release_date(scraper)
            prices = get_prices(scraper, link)
            games_data.append(GamePrice(title=title, prices=prices))
    except Exception as e:
        # attach partial progress and re-raise as our custom exception
        raise PartialResultsError(
            f"Collection interrupted after {len(games_data)} / {len(links)} games.",
            results=games_data,
            cause=e,
        ) from e
    return games_data


def main():
    output_file = "prices.json"
    try:
        links = get_games_pages(SimpleScraper(BASE_URL), GAMES_NO)
        scraper = Scraper(CATEGORIES_URL, timeout=TIMEOUT, proxy=PROXY)
        prices = collect_games_price(scraper, links)
    except Exception as e:
        print(f"Recovered {len(e.results)} partial results after error: {e}")
        with open(output_file, "w") as f:
            json.dump(
                [item.model_dump() for item in e.results], f, separators=(",", ":")
            )
        raise
    with open(output_file, "w") as f:
        json.dump([item.model_dump() for item in prices], f, separators=(",", ":"))


if __name__ == "__main__":
    main()
