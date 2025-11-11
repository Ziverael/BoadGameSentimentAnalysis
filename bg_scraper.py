import json
from typing import Final

from pydantic import BaseModel
from tqdm import tqdm

from src.collect.details import (
    GameFullDetail,
    GameStats,
    collect_community_stats,
    collect_game_info,
)
from src.collect.reviews import ReviewInfo, collect_reviews
from src.dynamic_scraper import Scraper
from src.scraper import SimpleScraper


BASE_URL: Final[str] = "https://boardgamegeek.com"
CATEGORIES_URL: Final[str] = f"{BASE_URL}/browse/boardgamecategory"
GAMES_URL: Final[str] = "https://boardgamegeek.com/browse/boardgame"
TIMEOUT: Final[int] = 10
PROXY: Final[str | None] = None
GAMES_NO: int = 500


class Game(BaseModel):
    title: str
    game_details: GameFullDetail
    game_stats: GameStats
    game_reviews: list[ReviewInfo]


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


def get_anchors_from_first_table(scraper: Scraper) -> list[str]:
    table = scraper.scrape("table", get_text=False, all_results=False)
    return scraper.scrape(
        "a",
        parent=table,
    )


class PartialResultsError(Exception):
    """Raised when data collection fails but partial results are available."""

    def __init__(self, message: str, results: list, cause: Exception | None = None):
        super().__init__(message)
        self.results = results
        self.__cause__ = cause


def collect_games_data(scraper: Scraper, links: list[str]):
    games_data: list[Game] = []
    try:
        for link in tqdm(links):
            game_info = collect_game_info(scraper, link)
            game_title = game_info.title
            game = Game(
                title=game_title,
                game_details=game_info,
                game_stats=collect_community_stats(scraper, link),
                game_reviews=collect_reviews(game_info.id),
            )
            games_data.append(game)
    except Exception as e:
        # attach partial progress and re-raise as our custom exception
        raise PartialResultsError(
            f"Collection interrupted after {len(games_data)} / {len(links)} games.",
            results=games_data,
            cause=e,
        ) from e
    return games_data


def main():
    try:
        links = get_games_pages(SimpleScraper(BASE_URL), GAMES_NO)
        scraper = Scraper(CATEGORIES_URL, timeout=TIMEOUT, proxy=PROXY)
        categories = get_anchors_from_first_table(scraper)
        games = collect_games_data(scraper, links)
    except Exception as e:
        print(f"Recovered {len(e.results)} partial results after error: {e}")
        with open("games.json", "w") as f:
            json.dump(
                [item.model_dump() for item in e.results], f, separators=(",", ":")
            )
        raise


if __name__ == "__main__":
    main()

    # tags = set()
    # try:
    # for link in games_links:
    #     # Try connection for every single link
    #     try:
    #     #Get page
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

    # # Raise exception if connection failed
    # # ---------
