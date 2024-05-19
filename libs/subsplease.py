import asyncio
import hashlib
import os
from itertools import count
from traceback import format_exc

import anitopy
from feedparser import parse

from database import LOGS, DataBase


class SubsPlease:
    def __init__(self, dB: DataBase):
        self.db = dB

    def digest(self, string: str):
        return hashlib.md5(string.encode()).hexdigest()

    def _exit(self):
        LOGS.info("Stopping The Bot...")
        try:
            [os.system(f"rm -rf {fold}") for fold in ["downloads", "thumbs", "encode"]]
        except BaseException:
            LOGS.error(format_exc())
        exit()

    def rss_feed_data(self):
        try:
            return parse("https://subsplease.org/rss/?r=1080"), parse("https://subsplease.org/rss/?r=720"), parse("https://subsplease.org/rss/?r=sd")
        except KeyboardInterrupt:
            self._exit()
        except BaseException:
            LOGS.error(format_exc())
            return None, None

    def feed_optimizer(self):
        d1080, d720, dsd = self.rss_feed_data()
        if not d1080 or not d720 or not dsd:
            return None
        for i in range(min(len(d1080.entries), len(d720.entries), len(dsd.entries)) - 1, -1, -1):
            try:
                f1080, f720 ,fsd = d1080.entries[i], d720.entries[i], dsd.entries[i]
                a1080, a720, asd= (anitopy.parse(f1080.title)).get("anime_title"), (anitopy.parse(f720.title)).get("anime_title"), (
                    anitopy.parse(fsd.title)
                ).get("anime_title")
                if a1080 == a720 or a1080 == asd:
                    if "[Batch]" in f1080.title or "[Batch]" in f720.title or "[Batch]" in fsd.title:
                        continue
                    uid = self.digest(f1080.title + f720.title + fsd.title)
                    if not self.db.is_anime_uploaded(uid):
                        return {"uid": uid, "1080p": f1080, "720p": f720, "480p": fsd}
            except BaseException:
                LOGS.error(format_exc())
                return None

    async def on_new_anime(self, function):
        for i in count():
            data = self.feed_optimizer()
            if data:
                await function(data)
                self.db.add_anime(data.get("uid"))
            await asyncio.sleep(5)
