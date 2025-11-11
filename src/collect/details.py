import re

from pydantic import BaseModel

from src.dynamic_scraper import Scraper


class GameParams(BaseModel):
    age: str
    time: str
    players: str
    weight: float


class GameFullDetail(BaseModel):
    id: int
    title: str
    release: str
    long_description: str
    short_description: str
    params: GameParams


def collect_game_info(scraper: Scraper, game_page_url: str):
    scraper.set_page(game_page_url)
    params_raw = scraper.scrape("p", class_="gameplay-item-primary", get_text=False)
    params = get_game_params(params_raw)
    title, release = get_title_and_release_date(scraper)
    return GameFullDetail(
        id=get_game_id(game_page_url),
        title=title,
        release=release,
        long_description=get_long_description(scraper),
        short_description=get_short_description(scraper),
        params=params,
    )


def get_game_id(link: str) -> int:
    return int(link.split("/")[4])


def get_game_params(params: list[str]) -> GameParams:
    words = [re.split(r"[\t ]+", p.get_text()) for p in params]
    cleaned_params = [list(filter(lambda t: t != "", w)) for w in words]
    return GameParams(
        players=cleaned_params[0][0],
        time=cleaned_params[1][0],
        age=cleaned_params[2][1],
        weight=float(cleaned_params[3][2]),
    )


def get_title_and_release_date(scraper: Scraper) -> tuple[str, str]:
    title_div = scraper.scrape("div", class_="game-header-title-info", get_text=False)[
        1
    ]
    title_raw = scraper.scrape("h1", parent=title_div, get_text=True, all_results=False)
    return get_title(title_raw), get_release(title_raw)


def get_title(title_raw: str) -> str:
    title = re.sub(r"\t+", "", title_raw)
    title = re.sub(r" +\(\d+\) +", "", title)
    return re.sub(r"^ +", "", title)


def get_release(title_raw: str) -> str:
    title = re.sub(r"\t+", "", title_raw)
    release = re.findall(r"\(.+\)", title)[0]
    return re.sub(r"[\(\)]", "", release)


def get_short_description(scraper: Scraper) -> str:
    short_desc_div = scraper.scrape(
        "div", class_="game-header-title-container", get_text=False
    )[1]
    return scraper.scrape("p", parent=short_desc_div, all_results=False)


def get_long_description(scraper: Scraper) -> str:
    long_desc = scraper.scrape("article", class_="game-description-body")[0]
    return re.sub(r"([\t ]+$)|(\n)", "", long_desc)
