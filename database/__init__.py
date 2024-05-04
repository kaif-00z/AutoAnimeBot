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

from traceback import format_exc

from redis import Redis

from functions.config import Var
from libs.logger import LOGS


class DataBase:
    def __init__(self):
        try:
            LOGS.info("Trying Connect With Redis database")
            redis_info = Var.REDIS_URI.split(":")
            self.dB = Redis(
                host=redis_info[0],
                port=redis_info[1],
                password=Var.REDIS_PASS,
                charset="utf-8",
                decode_responses=True,
            )
            LOGS.info("Successfully Connected to Redis database")
        except Exception as error:
            LOGS.exception(format_exc())
            LOGS.critical(str(error))
            exit()
        self.cache = {}
        self.re_cache()

    def add_anime(self, name):
        data = self.cache.get("ANIMES_UPLOADED") or []
        if name not in data:
            data.append(name)
            self.cache["ANIMES_UPLOADED"] = data
            self.dB.set("ANIMES_UPLOADED", str(data))

    def toggle_original_upload(self):
        data = self.cache.get("OG_UPLOAD") or False
        if data:
            data = False
        else:
            data = True
        self.cache["OG_UPLOAD"] = data
        self.dB.set("OG_UPLOAD", str(data))

    def is_original_upload(self):
        return self.cache.get("OG_UPLOAD") or False

    def toggle_button_upload(self):
        data = self.cache.get("BUTTON_UPLOAD") or False
        if data:
            data = False
        else:
            data = True
        self.cache["BUTTON_UPLOAD"] = data
        self.dB.set("BUTTON_UPLOAD", str(data))

    def is_button_upload(self):
        return self.cache.get("BUTTON_UPLOAD") or False

    def is_anime_uploaded(self, name):
        data = self.cache.get("ANIMES_UPLOADED") or []
        if name in data:
            return True
        return False

    def get_anime_uploaded_list(self):
        return self.cache.get("ANIMES_UPLOADED") or []

    def store_items(self, _hash, list):
        data = self.cache.get("FILESTORE") or {}
        data.update({_hash: list})
        self.cache["FILESTORE"] = data
        self.dB.set("FILESTORE", str(data))

    def get_store_items(self, _hash):
        data = self.cache.get("FILESTORE") or {}
        if data.get(_hash):
            return data[_hash]
        return []

    def re_cache(self):
        for key in self.dB.keys():
            self.cache.update({key: eval(self.dB.get(key) or "[]")})
        LOGS.info(f"Succesfully Sync Database!!!")
