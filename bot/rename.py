#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2023 Kaif_00z
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
# License can be found in <
# https://github.com/kaif-00z/AutoAnimeBOt/blob/main/LICENSE > .

import anitopy
from pymalscraper.scraper import Scraper


def get_english(anime_name):
    try:
        scraper = Scraper()
        anime = scraper.get_anime(anime_name)
        x = anime.english_title
        return x.strip() or anime_name
    except BaseException:
        return anime_name


def _rename(name, og=None):
    try:
        data = anitopy.parse(name)
        anime_name = data.get("anime_title")
        if anime_name and data.get("episode_number"):
            return f"[S{data.get('anime_season') or 1}-{data.get('episode_number') or ''}] {get_english(anime_name)} [{data.get('video_resolution').replace('p', 'px246' if og else 'px256') or ''}] @ensembly.{data.get('file_extension') or 'mkv'}"
        if anime_name:
            return f"{get_english(anime_name)} [{data.get('video_resolution').replace('p', 'px264' if og else 'px256') or ''}] @ensembly.{data.get('file_extension') or 'mkv'}"
        return name
    except BaseException:
        return name
