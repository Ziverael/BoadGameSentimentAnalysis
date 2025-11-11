import math
from time import sleep
from typing import Any, Final

import requests
from pydantic import BaseModel
from retry import retry
from tqdm import tqdm


REQUEST_DELAY: Final[int] = 5
DEFAULT_REQUEST_TIMEOUT: Final[int] = 10


class ReviewInfo(BaseModel):
    review: str
    reviewer_country: str
    rating: float
    date: str
    is_owner: bool


def get_review_url(game_id: int, page: int) -> str:
    return f"https://api.geekdo.com/api/collections?ajax=1&comment=1&objectid={game_id}&objecttype=thing&oneperuser=0&pageid={page}&require_review=true&showcount=100"


@retry(
    (requests.exceptions.RequestException,),
    tries=10,
    delay=5,
    max_delay=60,
    backoff=2,  # exponential backoff multiplier
)
def get_review_response(url: str):
    res = requests.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)
    res.raise_for_status()
    return res.json()


def collect_reviews(game_id: int, pages_limit: int | None = None) -> list[ReviewInfo]:
    data = get_review_response(get_review_url(game_id, 0))
    comments_count = data["config"]["numitems"]
    pages = math.ceil(comments_count / 100) - 1 if pages_limit is None else pages_limit
    reviews: list[ReviewInfo] = []
    reviews.extend(get_reviews_from_page(data))
    for page_no in tqdm(range(pages)):
        reviews.extend(
            get_reviews_from_page(get_review_response(get_review_url(game_id, page_no)))
        )
        sleep(REQUEST_DELAY)
    return reviews


def get_reviews_from_page(data: dict[str, Any]) -> list[ReviewInfo]:
    return list(map(get_review, data["items"]))


def get_review(data: dict[str, Any]) -> ReviewInfo:
    return ReviewInfo(
        reviewer_country=data["user"]["country"],
        is_owner=data["status"].get("own", False),
        rating=data["rating"],
        date=data["postdate"],
        review=data["textfield"]["comment"]["value"],
    )
