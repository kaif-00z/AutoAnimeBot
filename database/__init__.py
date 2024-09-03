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

from functions.config import Var
from libs.firebasewarp import FireDB
from libs.logger import LOGS

import sys

class DataBase:
    def __init__(self):
        try:
            LOGS.info("Trying Connect With Firebase Database")
            self.dB = FireDB(Var)
            LOGS.info("Successfully Connected to Firebase Database")
        except Exception as error:
            LOGS.exception(format_exc())
            LOGS.critical(str(error))
            sys.exit(1)
        self.cache = self.dB.getall()
        LOGS.info(f"Succesfully Sync Database!!!")

    def add_anime(self, name):
        data = self.cache.get("ANIMES_UPLOADED") or []
        if name not in data:
            data.append(name)
            self.cache["ANIMES_UPLOADED"] = data
            self.dB.create_data("ANIMES_UPLOADED", data)

    def toggle_separate_channel_upload(self):
        data = self.cache.get("SEPARATE_CHANNEL_UPLOAD") or False
        if data:
            data = False
        else:
            data = True
        self.cache["SEPARATE_CHANNEL_UPLOAD"] = data
        self.dB.create_data("SEPARATE_CHANNEL_UPLOAD", data)

    def is_separate_channel_upload(self):
        return self.cache.get("SEPARATE_CHANNEL_UPLOAD") or False

    def toggle_original_upload(self):
        data = self.cache.get("OG_UPLOAD") or False
        if data:
            data = False
        else:
            data = True
        self.cache["OG_UPLOAD"] = data
        self.dB.create_data("OG_UPLOAD", data)

    def is_original_upload(self):
        return self.cache.get("OG_UPLOAD") or False

    def toggle_button_upload(self):
        data = self.cache.get("BUTTON_UPLOAD") or False
        if data:
            data = False
        else:
            data = True
        self.cache["BUTTON_UPLOAD"] = data
        self.dB.create_data("BUTTON_UPLOAD", data)

    def is_button_upload(self):
        return self.cache.get("BUTTON_UPLOAD") or False

    def is_anime_uploaded(self, name):
        data = self.cache.get("ANIMES_UPLOADED") or []
        if name in data:
            return True
        return False

    def add_anime_channel_info(self, title, _data):
        data = self.cache.get("ANIME_CHANNEL_INFO") or {}
        data.update({title: _data})
        self.cache["ANIME_CHANNEL_INFO"] = data
        self.dB.create_data(f"ANIME_CHANNEL_INFO/{title}", _data)

    def get_anime_channel_info(self, title):
        data = self.cache.get("ANIME_CHANNEL_INFO") or {}
        if data.get(title):
            return data[title]
        return {}

    def get_anime_uploaded_list(self):
        return self.cache.get("ANIMES_UPLOADED") or []

    def store_items(self, _hash, _list):
        data = self.cache.get("FILESTORE") or {}
        data.update({_hash: _list})
        self.cache["FILESTORE"] = data
        self.dB.create_data(f"FILESTORE/{_hash}", _list)

    def get_store_items(self, _hash):
        data = self.cache.get("FILESTORE") or {}
        if data.get(_hash):
            return data[_hash]
        return []

    def add_broadcast_user(self, user_id):
        data = self.cache.get("BROADCAST") or []
        if user_id not in data:
            data.append(int(user_id))
            self.cache["BROADCAST"] = data
            self.dB.create_data("BROADCAST", data)

    def get_broadcast_user(self):
        return self.cache.get("BROADCAST") or []
