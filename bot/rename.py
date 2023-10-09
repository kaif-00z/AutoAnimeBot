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
# https://github.com/kaif-00z/AutoAnimeBot/blob/main/LICENSE > .

import anitopy
from AnilistPython import Anilist

from .func import run_async

anilist = Anilist()

CAPTION = """
<strong>{}</strong>

{}
"""


@run_async
def get_english(anime_name):
    try:
        anime = anilist.get_anime(anime_name)
        x = anime.get("name_english")
        return x.strip() or anime_name
    except Exception as error:
        print(error)
        return anime_name.strip()


@run_async
def get_poster(name):
    try:
        anime_name = get_proper_name_for_func(name)
        if anime_name:
            anime_id = anilist.get_anime_id(anime_name)
            return f"https://img.anili.st/media/{anime_id}"
    except Exception as error:
        print(error)
        return None


@run_async
def get_caption(name):
    try:
        anime_name = get_proper_name_for_func(name)
        if anime_name:
            anime = anilist.get_anime(anime_name)
            desc = anime.get("desc").strip()
            return CAPTION.format(
                anime.get("name_english").strip() or "",
                desc if len(desc) < 763 else desc[:760] + "...",
            )
    except BaseException:
        return ""


@run_async
def get_cover(name):
    try:
        anime_name = get_proper_name_for_func(name)
        if anime_name:
            anime = anilist.get_anime(anime_name)
            return anime.get("cover_image")
    except Exception as error:
        print(error)
        return None


def get_proper_name_for_func(name):
    try:
        data = anitopy.parse(name)
        anime_name = data.get("anime_title")
        if anime_name and data.get("episode_number"):
            return (
                f"{anime_name} S{data.get('anime_season')}"
                if data.get("anime_season")
                else anime_name
            )
        return anime_name
    except BaseException:
        return None


async def _rename(name, og=None):
    try:
        data = anitopy.parse(name)
        anime_name = data.get("anime_title")
        if anime_name and data.get("episode_number"):
            return (
                f"[AF] [S{data.get('anime_season') or 1}-{data.get('episode_number') or ''}] {(await get_english(anime_name))} [{data.get('video_resolution').replace('p', 'px264' if og else 'px265') or ''}].mkv".replace(
                    "‘", ""
                )
                .replace("’", "")
                .strip()
            )
        if anime_name:
            return (
                f"[AF] {(await get_english(anime_name))} [{data.get('video_resolution').replace('p', 'px264' if og else 'px265') or ''}].mkv".replace(
                    "‘", ""
                )
                .replace("’", "")
                .strip()
            )
        return name
    except Exception as error:
        print(error)
        return name
