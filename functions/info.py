#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2025 Kaif_00z
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

from traceback import format_exc

import anitopy

from libs.kitsu import RawAnimeInfo
from libs.logger import LOGS


class AnimeInfo:
    def __init__(self, name):
        self.kitsu = RawAnimeInfo()
        self.CAPTION = """
**{}
━━━━━━━━━━━━━━━
‣ Language:** `Japanese [ESub]`
**‣ Quality:** `480p|720p|1080p`
**‣ Season:** `{}`
**‣ Episode:** `{}`
**━━━━━━━━━━━━━━━**
"""
        self.proper_name = self.get_proper_name_for_func(name)
        self.name = name
        self.data = anitopy.parse(name)

    async def get_english(self):
        anime_name = self.data.get("anime_title")
        try:
            anime = (await self.kitsu.search(self.proper_name)) or {}
            return anime.get("english_title") or anime_name
        except BaseException:
            LOGS.error(str(format_exc()))
            return anime_name.strip()

    async def get_poster(self):
        try:
            if self.proper_name:
                anime_poster = await self.kitsu.search(self.proper_name)
                return anime_poster.get("poster_img") or None
        except BaseException:
            LOGS.error(str(format_exc()))

    async def get_cover(self):
        try:
            if self.proper_name:
                anime_poster = await self.kitsu.search(self.proper_name)
                if anime_poster.get("anilist_id"):
                    return anime_poster.get("anilist_poster")
                return None
        except BaseException:
            LOGS.error(str(format_exc()))

    async def get_caption(self):
        try:
            if self.proper_name or self.data:
                return self.CAPTION.format(
                    (await self.get_english()),
                    str(self.data.get("anime_season") or 1).zfill(2),
                    (
                        str(self.data.get("episode_number")).zfill(2)
                        if self.data.get("episode_number")
                        else "N/A"
                    ),
                )
        except BaseException:
            LOGS.error(str(format_exc()))
            return ""

    async def rename(self, original=False):
        try:
            anime_name = self.data.get("anime_title")
            if anime_name and self.data.get("episode_number"):
                return (
                    f"[S{self.data.get('anime_season') or 1}-{self.data.get('episode_number') or ''}] {(await self.get_english())} [{self.data.get('video_resolution')}].mkv".replace(
                        "‘", ""
                    )
                    .replace("’", "")
                    .strip()
                )
            if anime_name:
                return (
                    f"{(await self.get_english())} [{self.data.get('video_resolution')}].mkv".replace(
                        "‘", ""
                    )
                    .replace("’", "")
                    .strip()
                )
            return self.name
        except Exception as error:
            LOGS.error(str(error))
            LOGS.exception(format_exc())
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
            LOGS.exception(format_exc())
