from dataclasses import asdict
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from loguru import logger

from models import Anime, TypeAnime



def get_data(url_page, type_anime: TypeAnime):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }

    animes_data_list: list[Anime] = []

    folder_catalog = "catalogs"
    folder_data = "data"
    folder_films: TypeAnime = "films"
    folder_serials: TypeAnime = "serials"

    if not os.path.exists(folder_catalog):
        os.mkdir(folder_catalog)

    if not os.path.exists(folder_data):
        os.mkdir(folder_data)

    if not os.path.exists(folder_films):
        os.mkdir(folder_films)

    if not os.path.exists(folder_serials):
        os.mkdir(folder_serials)


    # Запрос на сайт

    # req = requests.get(url_page, headers=headers)
    # with open(f"{folder_catalog}/anime_{type_anime}_top_100.html", "w", encoding="utf-8") as file:
    #     file.write(req.text)


    logger.debug("Сохранение страницы в папку catalogs")
    # Открыли из сохраненной страницы
    with open(f"{folder_catalog}/anime_{type_anime}_top_100.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    animes = soup.find_all("div", class_="anime-column")

    logger.debug("Обход карточек из каталога")
    for anime in animes:
        url = "https://yummy-anime.ru" + anime.find("a").get("href")
        img = "https:" + anime.find("img").get("src")
        title = anime.find("div", class_="anime-column-info").find("a").text.strip()
        views = anime.find("div", class_="icons-row").find("div", class_="views-count").text
        rating = anime.find("div", class_="rating-bottom").text.strip()
        
        logger.debug(f"Добавление первичных данных в список, Аниме '{title}'")
        animes_data_list.append(Anime(url=url, img=img, title=title, views=views, rating=rating, top_rang=None, type_anime=None, age_rating=None, genres=None, release_year=None, studios=None, directors=None, episodes=None))

    logger.debug("Обход страниц по ссылкам карточек")
    for anime in animes_data_list:

        # Запрос на сайт
        req = requests.get(anime.url, headers=headers)
        page_name = anime.url.split("/")[-1]
    
        logger.debug("Запись страницы в в файл")
        with open(f"{type_anime}/{page_name}.html", "w", encoding="utf-8") as file:
            file.write(req.text)

        with open(f"{type_anime}/{page_name}.html", encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        anime_data = soup.find("div", class_="content-page bordered-overflow anime-content-page")

        logger.debug("Сбор оставшихся данных со страницы...")
        logger.info(f"Аниме '{anime.title}'")
        try:
            anime.top_rang = anime_data.find("div", class_="saw position top-rating").text.strip().split(" ")[0].strip()
        except Exception:
            logger.warning("Место в топе не найдено")
            anime.top_rang = None

        content_info = anime_data.find("ul", class_="content-main-info")

        try:
            anime.type_anime = content_info.find("li", {"id": "animeType"}).text.strip()
        except Exception:
            logger.warning("Тип аниме не найден")
            anime.type_anime = None

        try:
            anime.release_year = content_info.find("span", string=re.compile('Год выхода:')).find_next("div").text.strip()
        except Exception:
            logger.warning("Год выхода не найден")
            anime.release_year = None

        try:
            anime.age_rating = content_info.find("li", class_="first-line-info categories-list").find("a")['data-balloon']
        except Exception:
            logger.warning("Возрастной рейтинг не найден")
            anime.age_rating = None

        try:
            anime.genres = [genres.text.strip() for genres in content_info.find("li", class_="categories-list no-comma").find("ul").find_all("li")]
        except Exception:
            logger.warning("Жанры не найдены")
            anime.genres = None
        
        try:
            anime.studios = [studios.text.strip() for studios in content_info.find("span", class_="studio").find_next("ul").find_all("li")]
        except Exception:
            logger.warning("Студия не найдена")
            anime.studios = None

        try:
            anime.directors = [directors.text.strip() for directors in content_info.find("span", class_="creator").find_next("ul").find_all("li")]
        except Exception:
            logger.warning("Режисёр не найден")
            anime.directors = None
        
        try:
            anime.episodes = content_info.find("span", string=re.compile('Количество серий:')).find_next("div").text.strip()
        except Exception:
            logger.warning("Количество эпизодов не найдено")
            anime.episodes = None
        
        logger.info(f"Сбор инормации по аниме '{anime.title}' завершён")

        # print(anime.__dict__)

    anime_dicts = [asdict(anime) for anime in animes_data_list]

    logger.debug("Запись списка в json файл")

    with open(f"{folder_data}/anime_{type_anime}_top_100.json", "w", encoding="utf-8") as file:
        json.dump(anime_dicts, file, indent=4, ensure_ascii=False)
        logger.info("Работа завершена!")

        
    
def run():
    # logger.add(sys.stdout, format="{time} | {level} | {} | {message}", level="DEBUG")

    get_data("https://yummy-anime.ru/catalog/top?sort=serials", "serials")
    print("--" * 20)
    get_data("https://yummy-anime.ru/catalog/top?sort=films", "films")


if __name__ == "__main__":
    run()