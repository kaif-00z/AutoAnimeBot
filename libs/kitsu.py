#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2026 Kaif_00z
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
from difflib import SequenceMatcher
from urllib.parse import quote

import aiohttp
from AnilistPython import Anilist

ORDINALS = {
    2: "2nd",
    3: "3rd",
    4: "4th",
    5: "5th",
    6: "6th",
    7: "7th",
    8: "8th",
    9: "9th",
    10: "10th",
}


def normalize(text):
    text = re.sub(r"[^\w\s]", "", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def extract_season(query):
    m = re.search(r"\bS(\d+)\b", query, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"\bSeason\s*(\d+)\b", query, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def strip_season(query):
    query = re.sub(r"\s+S\d+.*$", "", query, flags=re.IGNORECASE)
    query = re.sub(r"\s+Season\s*\d+.*$", "", query, flags=re.IGNORECASE)
    return query.strip()


def season_bonus(title, season_num):
    lower = title.lower()
    if not season_num or season_num <= 1:
        has_marker = bool(
            re.search(r"\b(2nd|3rd|\d+th)\s+season\b", lower)
            or re.search(r"\bseason\s*\d+\b", lower)
            or re.search(r"\bpart\s*[2-9]\b", lower)
        )
        return 0.25 if not has_marker else 0.0
    indicators = [f"season {season_num}", f"part {season_num}"]
    ordinal = ORDINALS.get(season_num)
    if ordinal:
        indicators.append(f"{ordinal} season")
    indicators.append(str(season_num))
    for ind in indicators:
        if ind in lower:
            return 0.35
    return 0.0


def is_relevant(attrs):
    status = attrs.get("status", "")
    if status == "tba":
        return False
    if status == "current":
        return True
    current_year = datetime.now().year
    ok_years = {str(y) for y in range(current_year - 2, current_year + 2)}
    end_date = attrs.get("endDate") or ""
    start_date = attrs.get("startDate") or ""
    if not end_date and not start_date:
        return False
    return any(y in end_date or y in start_date for y in ok_years)


class RawAnimeInfo:
    def __init__(self):
        self.anilist = Anilist()

    async def search(self, query: str):
        raw_data = ((await self.searcher(query)) or {}).get("data") or {}
        try:
            _raw_data = await self.search_anilist(raw_data.get("id"))
        except Exception:
            _raw_data = {}
        if not raw_data:
            return {}
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
        data["status"] = raw_data.get("attributes", {}).get("status") or "unknown"
        data["start_date"] = raw_data.get("attributes", {}).get("startDate")
        data["end_date"] = raw_data.get("attributes", {}).get("endDate")
        return {**(data if data else {}), **(_raw_data if _raw_data else {})}

    async def searcher(self, query: str):
        season_num = extract_season(query)
        base_query = strip_season(query)

        search_queries = [query]
        if base_query.lower() != query.lower():
            search_queries.append(base_query)
        if season_num and season_num > 1:
            ordinal = ORDINALS.get(season_num)
            if ordinal:
                search_queries.append(f"{base_query} {ordinal} season")

        async with aiohttp.ClientSession() as client:
            try:
                seen_ids = set()
                all_results = []

                for sq in search_queries:
                    data = await client.get(
                        f"https://kitsu.io/api/edge/anime?filter[text]={quote(sq)}"
                        "&page[limit]=10"
                    )
                    entries = (await data.json()).get("data", [])
                    for entry in entries:
                        eid = entry.get("id")
                        if eid and eid not in seen_ids:
                            seen_ids.add(eid)
                            all_results.append(entry)

                best_match = None
                best_score = -1.0

                for entry in all_results:
                    detail = await self._fetch_detail(client, entry)
                    if not detail:
                        continue
                    attrs = detail["data"]["attributes"]
                    if not is_relevant(attrs):
                        continue
                    titles = attrs.get("titles", {})
                    candidates = list(
                        filter(
                            None,
                            [
                                titles.get("en"),
                                titles.get("en_jp"),
                                titles.get("ja_jp"),
                                attrs.get("canonicalTitle"),
                                *(attrs.get("abbreviatedTitles") or []),
                            ],
                        )
                    )
                    if not candidates:
                        continue
                    score = max(similarity(base_query, t) for t in candidates) + max(
                        season_bonus(t, season_num) for t in candidates
                    )
                    if score > best_score:
                        best_score = score
                        best_match = detail

                if best_match:
                    return best_match

                for entry in all_results:
                    detail = await self._fetch_detail(client, entry)
                    if detail and detail["data"]["attributes"].get("status") != "tba":
                        return detail
            except Exception:
                raise ValueError("Kitsu: Search Link Not Found")

    async def _fetch_detail(self, client, entry):
        link = entry.get("links", {}).get("self")
        if not link:
            return None
        try:
            resp = await client.get(link)
            return await resp.json()
        except Exception:
            return None

    async def re_searcher(self, link: str):
        if not link:
            raise ValueError("Kitsu: Link Not Found")
        async with aiohttp.ClientSession() as client:
            try:
                data = await client.get(link)
                return await data.json()
            except Exception:
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
            except Exception:
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
        except Exception:
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
