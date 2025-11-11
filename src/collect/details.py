import re
from functools import reduce
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.dynamic_scraper import Scraper


class GameParams(BaseModel):
    age: str
    time: str
    players: str
    weight: float


def alias_generator(field_name: str) -> str:
    return re.sub(r"_", " ", field_name).title()


class GameStats(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generator, populate_by_name=True)

    avg_rating: float = Field(alias="Avg. Rating")
    no_of_ratings: str = Field(alias="No. of Ratings")
    std_deviation: float = Field(alias="Std. Deviation")
    weight: str
    comments: str
    fans: str
    page_views: str
    overall_rank: str
    strategy_rank: str
    all_time_plays: str
    this_month: str
    own: str
    prev_owned: str = Field(alias="Prev. Owned")
    for_trade: str
    want_in_trade: str
    wishlist: str
    has_parts: str
    want_parts: str


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


def collect_community_stats(scraper: Scraper, game_url: str):
    scraper.set_page(f"{game_url}/stats")
    stats_pane = scraper.scrape("div", class_="game-stats", get_text=False)[0]
    raw_stats = scraper.scrape("li", parent=stats_pane)
    mapped = map(get_key_vaule_stats_from_li, raw_stats)
    reduced = reduce(lambda x, y: x | y, mapped)
    return GameStats(**reduced)


stat_field_regex = re.compile(r"(\S[\w\s.-]+?)\s+([\d.,\s/]+[\d]+)[\s\w-]*$")


def get_key_vaule_stats_from_li(text: str) -> dict[str, Any]:
    match = stat_field_regex.search(text)
    return {match.group(1).strip(): match.group(2)} if match else {}
