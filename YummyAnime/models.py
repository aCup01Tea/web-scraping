from dataclasses import dataclass
from typing import Literal


@dataclass
class Anime:
    url: str | None
    img: str | None
    title: str | None
    views: str | None
    rating: str | None
    top_rang: str | None
    type_anime: str | None
    age_rating: str | None
    genres: list[str] | None
    release_year: str | None
    studios: list[str] | None
    directors: list[str] | None
    episodes: str | None

TypeAnime = Literal["films", "serials"]