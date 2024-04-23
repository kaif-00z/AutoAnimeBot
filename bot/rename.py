#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2023-24 Kaif_00z
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

import anitopy, re, pytz
from kitsu import AnimeInfo
from datetime import datetime

kitsu = AnimeInfo()

CAPTION = """
**〄 {} • {}
━━━━━━━━━━━━━━━
⬡ Quality: 720p, 1080p
⬡ Audio: Japanese [English Subtitles]
⬡ Genres: {}  
━━━━━━━━━━━━━━━
〣 Next Airing Episode: {}  
〣 Next Airing Episode Date: {}  
━━━━━━━━━━━━━━━**
〣 #{}
"""

async def get_english(name):
    data = anitopy.parse(name)
    anime_name = data.get("anime_title")
    try:
        anime = await kitsu.search(get_proper_name_for_func(name))
        x = anime.get("english_title")
        return x.strip() or anime_name
    except Exception as error:
        print(error)
        return anime_name.strip()

async def get_poster(name):
    try:
        anime_name = get_proper_name_for_func(name)
        if anime_name:
            anime_poster = await kitsu.search(anime_name)
            return anime_poster.get("poster_img") or None
    except Exception as error:
        print(error)
        return None

async def get_cover(name):
    try:
        anime_name = get_proper_name_for_func(name)
        if anime_name:
            anime_poster = await kitsu.search(anime_name)
            if anime_poster.get("anilist_id"):
                return anime_poster.get("anilist_poster")
            return None
    except Exception as error:
        print(error)
        return None

async def get_caption(name):
    try:
        anime_name = get_proper_name_for_func(name)
        if anime_name:
            anime = await kitsu.search(anime_name)
            next_ = anime.get('next_airing_ep', {})
            return CAPTION.format(
                anime.get("english_title").strip() or "",
                anime.get("type"),
                ", ".join(anime.get("genres")),
                next_.get("episode") or "N/A",
                datetime.fromtimestamp(next_.get("airingAt"), tz=pytz.timezone("Asia/Kolkata")).strftime("%A, %B %d, %Y"),
                "".join(re.split("[^a-zA-Z]*", anime.get("english_title") or ""))
            )
    except BaseException:
        return ""

def get_proper_name_for_func(name):
    try:
        data = anitopy.parse(name)
        anime_name = data.get("anime_title")
        if anime_name and data.get("episode_number"):
            return (
                f"{anime_name} S{data.get('anime_season')} {data.get('episode_title')}" if data.get("anime_season") and data.get("episode_title") else f"{anime_name} S{data.get('anime_season')}" if data.get("anime_season") else anime_name 
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
                f"[S{data.get('anime_season') or 1}-{data.get('episode_number') or ''}] {(await get_english(name))} [{data.get('video_resolution').replace('p', 'px264' if og else 'px265') or ''}].mkv".replace(
                    "‘", ""
                )
                .replace("’", "")
                .strip()
            )
        if anime_name:
            return (
                f"{(await get_english(name))} [{data.get('video_resolution').replace('p', 'px264' if og else 'px265') or ''}].mkv".replace(
                    "‘", ""
                )
                .replace("’", "")
                .strip()
            )
        return name
    except Exception as error:
        print(error)
        return name
