import math
from time import sleep
from typing import Any, Final

import requests
from pydantic import BaseModel


DEFAULT_REQUEST_TIMEOUT: Final[int] = 10


class ReviewInfo(BaseModel):
    review: str
    reviewer_country: str
    rating: float
    date: str
    is_owner: bool


def get_review_url(game_id: int, page: int) -> str:
    return f"https://api.geekdo.com/api/collections?ajax=1&comment=1&objectid={game_id}&objecttype=thing&oneperuser=0&pageid={page}&require_review=true&showcount=100"


def collect_reviews(
    game_id: int, sleep_time: float = 2.0, pages_limit: int | None = None
) -> list[ReviewInfo]:
    res = requests.get(get_review_url(game_id, 0), timeout=DEFAULT_REQUEST_TIMEOUT)
    data = res.json()
    comments_count = data["config"]["numitems"]
    pages = math.ceil(comments_count / 100) if pages_limit is None else pages_limit
    reviews: list[ReviewInfo] = []
    reviews.extend(get_reviews_from_page(data))
    for page_no in range(pages):
        res = requests.get(
            get_review_url(game_id, page_no), timeout=DEFAULT_REQUEST_TIMEOUT
        )
        reviews.extend(get_reviews_from_page(res.json()))
        sleep(sleep_time)
    return reviews


def get_reviews_from_page(data: dict[str, Any]) -> list[ReviewInfo]:
    return list(map(collect_reviews, data["items"]))


def get_review(data: dict[str, Any]) -> ReviewInfo:
    return ReviewInfo(
        reviewer_country=data["user"]["country"],
        is_owner=data["status"].get("own", False),
        rating=data["rating"],
        date=data["postdate"],
        review=data["textfield"]["comment"]["value"],
    )
