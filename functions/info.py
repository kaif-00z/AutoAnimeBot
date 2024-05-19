#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2024 Kaif_00z
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

# if you are using this following code then don't forgot to give proper
# credit to t.me/kAiF_00z (github.com/kaif-00z)

import re
from datetime import datetime

import anitopy
import pytz

from libs.kitsu import RawAnimeInfo
from libs.logger import LOGS


class AnimeInfo:
    def __init__(self, name):
        self.kitsu = RawAnimeInfo()
        self.CAPTION = """
⛩️ {} • {} • 🧭

┏━━━━━━━✦✗✦━━━━━━━━┓

• Quality: 480p, 720p, 1080p
• Audio: Japanese [English Subtitles]
• Genres: {}
• Status: Ongoing - 2024
• Next Week Episode: {}

┗━━━━━━━✦✗✦━━━━━━━━┛

🍁 Uρᥣoᥲdᥱd Bყ : @Anime_Compass 🧭
"""
        self.proper_name = self.get_proper_name_for_func(name)
        self.name = name
        self.data = anitopy.parse(name)

    async def get_english(self):
        anime_name = self.data.get("anime_title")
        try:
            anime = await self.kitsu.search(self.proper_name)
            return anime.get("english_title").strip() or anime_name
        except Exception as error:
            LOGS.error(str(error))
            return anime_name.strip()

    async def get_poster(self):
        try:
            if self.proper_name:
                anime_poster = await self.kitsu.search(self.proper_name)
                return anime_poster.get("poster_img") or None
        except Exception as error:
            LOGS.error(str(error))

    async def get_cover(self):
        try:
            if self.proper_name:
                anime_poster = await self.kitsu.search(self.proper_name)
                if anime_poster.get("anilist_id"):
                    return anime_poster.get("anilist_poster")
                return None
        except Exception as error:
            LOGS.error(str(error))

    async def get_caption(self):
        try:
            if self.proper_name:
                anime = await self.kitsu.search(self.proper_name)
                next_ = anime.get("next_airing_ep", {})
                return self.CAPTION.format(
                    anime.get("english_title").strip() or self.data.get("anime_title"),
                    anime.get("type"),
                    ", ".join(anime.get("genres")),
                    next_.get("episode") or "N/A",
                    (
                        datetime.fromtimestamp(
                            next_.get("airingAt"), tz=pytz.timezone("Asia/Kolkata")
                        ).strftime("%A, %B %d, %Y")
                        if next_.get("airingAt")
                        else "N/A"
                    ),
                    "".join(re.split("[^a-zA-Z]*", anime.get("english_title") or "")),
                )
        except Exception as error:
            LOGS.error(str(error))
            return ""

    async def rename(self, original=False):
        try:
            anime_name = self.data.get("anime_title")
            if anime_name and self.data.get("episode_number"):
                 return (
                    f"[AC🧭][S{self.data.get('anime_season') or 1}-{self.data.get('episode_number') or ''}] {(await self.get_english())} [{self.data.get('video_resolution') or ''}] @Anime_Compass.mkv".replace(
                        "‘", ""
                    )
                    .replace("’", "")
                    .strip()
                )
        except Exception as e:
        # Handle exceptions here
            pass    
  
            if anime_name:
                return (
                    f"[AC🧭][S{self.data.get('anime_season') or 1}-{self.data.get('episode_number') or ''}] {(await self.get_english())} [{self.data.get('video_resolution') or ''}] @Anime_Compass.mkv".replace(
                        "‘", ""
                    )
                    .replace("’", "")
                    .strip()
                )
            return self.name
        except Exception as error:
            LOGS.error(str(error))
            return self.name

    def get_proper_name_for_func(self, name):
        try:
            data = anitopy.parse(name)
            anime_name = data.get("anime_title")
            if anime_name and data.get("episode_number"):
                return (
                    f"{anime_name} S{data.get('anime_season')} {data.get('episode_title')}"
                    if data.get("anime_season") and data.get("episode_title")
                    else (
                        f"{anime_name} S{data.get('anime_season')}"
                        if data.get("anime_season")
                        else anime_name
                    )
                )
            return anime_name
        except Exception as error:
            LOGS.error(str(error))
