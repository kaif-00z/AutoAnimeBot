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

import aiohttp
from AnilistPython import Anilist


class RawAnimeInfo:
    def __init__(self):
        self.anilist = Anilist()

    async def search(self, query: str):
        raw_data = ((await self.searcher(query)) or {}).get("data") or {}
        try:
            _raw_data = await self.search_anilist(raw_data.get("id"))
        except BaseException:
            _raw_data = {}
        if not raw_data:
            data = {}  # self.alt_anilist(query)
            return data
        data = {}
        data["anime_id"] = raw_data.get("id")
        data["english_title"] = raw_data.get("attributes", {}).get("titles", {}).get(
            "en"
        ) or raw_data.get("attributes", {}).get("titles", {}).get("en_jp")
        data["japanese_title"] = (
            raw_data.get("attributes", {}).get("titles", {}).get("ja_jp")
        )
        data["description"] = raw_data.get("attributes", {}).get("description")
        data["total_eps"] = raw_data.get("attributes", {}).get("episodeCount") or "N/A"
        data["poster_img"] = (
            raw_data.get("attributes", {}).get("posterImage", {}).get("original")
        )
        # anilist score will be better i guess
        # data["score"] = raw_data.get("attributes", {}).get("averageRating") or "N/A"
        data["type"] = raw_data.get("attributes", {}).get("showType") or "TV"
        data["runtime"] = raw_data.get("attributes", {}).get("episodeLength") or 24
        return {**(data if data else {}), **(_raw_data if _raw_data else {})}

    async def searcher(
        self,
        query: str,
    ):
        async with aiohttp.ClientSession() as client:
            try:
                data = await client.get(
                    f"https://kitsu.io/api/edge/anime?filter%5Btext%5D={query.replace(' ', '%20')}"
                )
                links = (await data.json())["data"]
                for index in range(len(links)):
                    res_data = await self.re_searcher(links[index]["links"]["self"])
                    if res_data["data"]["attributes"]["status"] == "tba":
                        continue
                    if "current" != res_data["data"]["attributes"]["status"]:
                        if (
                            res_data["data"]["attributes"]["endDate"]
                            or res_data["data"]["attributes"]["startDate"]
                        ):
                            if "2025" not in (
                                res_data["data"]["attributes"]["endDate"] or ""
                            ):
                                if all(
                                    year
                                    not in (
                                        res_data["data"]["attributes"]["startDate"]
                                        or ""
                                    )
                                    for year in ["2024", "2025"]
                                ):
                                    continue
                    return res_data
            except BaseException:
                raise ValueError("Kitsu: Search Link Not Found")

    async def re_searcher(self, link: str):
        if not link:
            raise ValueError("Kitsu: Link Not Found")
        async with aiohttp.ClientSession() as client:
            try:
                data = await client.get(link)
                return await data.json()
            except BaseException:
                raise ValueError("Kitsu: Link Not Found")

    async def search_anilist(self, kitsu_id):
        if not kitsu_id:
            raise ValueError("Kitsu: ID Not Found")
        async with aiohttp.ClientSession() as client:
            try:
                _data = {}
                res = await client.get(
                    f"https://kitsu.io/api/edge/anime/{kitsu_id}/mappings"
                )
                data = (await res.json())["data"]
                for maps in data:
                    if (
                        maps.get("attributes", {}).get("externalSite")
                        == "anilist/anime"
                    ):
                        _data["anilist_id"] = maps.get("attributes", {}).get(
                            "externalId"
                        )
                        _data["anilist_poster"] = (
                            f"https://img.anili.st/media/{_data['anilist_id']}"
                        )
                        __data = self.anilist_result(_data["anilist_id"])
                        return {**_data, **__data}
            except BaseException:
                raise ValueError("Kitsu: Mapping Failed")

    def anilist_result(self, anilist_id):
        try:
            data = self.anilist.get_anime_with_id(anilist_id)
            return {
                "genres": data.get("genres"),
                "next_airing_ep": data.get("next_airing_ep"),
                "season": data.get("season"),
                "starting_time": data.get("starting_time"),
                "ending_time": data.get("ending_time"),
                "score": data.get("average_score") or "N/A",
            }
        except BaseException:
            return {}

    def alt_anilist(self, anime_name):
        data = self.anilist.get_anime(anime_name)
        _id = self.anilist.get_anime_id(anime_name)
        return {
            "anilist_id": _id,
            "genres": data.get("genres"),
            "next_airing_ep": data.get("next_airing_ep") or {},
            "season": data.get("season"),
            "starting_time": data.get("starting_time"),
            "ending_time": data.get("ending_time"),
            "score": data.get("average_score") or "N/A",
            "english_title": data.get("name_english"),
            "japanese_title": data.get("name_romaji"),
            "description": data.get("desc"),
            "total_eps": data.get("airing_episodes") or "N/A",
            "poster_img": data.get("banner_image"),
            "type": data.get("airing_format") or "TV",
            "runtime": 24,
            "anilist_poster": f"https://img.anili.st/media/{_id}",
        }
