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

import asyncio
import json
import os
import subprocess
from pathlib import Path
from traceback import format_exc

import aiofiles
import aiohttp
from html_telegraph_poster import TelegraphPoster

from functions.config import Var
from libs.logger import LOGS

OK = {}


class Tools:
    def __init__(self):
        pass

    async def async_searcher(
        self,
        url: str,
        post: bool = None,
        headers: dict = None,
        params: dict = None,
        json: dict = None,
        data: dict = None,
        ssl=None,
        re_json: bool = False,
        re_content: bool = False,
        real: bool = False,
        *args,
        **kwargs,
    ):
        async with aiohttp.ClientSession(headers=headers) as client:
            if post:
                data = await client.post(
                    url, json=json, data=data, ssl=ssl, *args, **kwargs
                )
            else:
                data = await client.get(url, params=params, ssl=ssl, *args, **kwargs)
            if re_json:
                return await data.json()
            if re_content:
                return await data.read()
            if real:
                return data
            return await data.text()

    async def cover_dl(self, link):
        try:
            image = await self.async_searcher(link, re_content=True)
            fn = f"thumbs/{link.split('/')[-1]}"
            if not fn.endswith((".jpg" or ".png")):
                fn += ".jpg"
            async with aiofiles.open(fn, "wb") as file:
                await file.write(image)
            return fn
        except Exception as error:
            LOGS.error(str(error))

    async def mediainfo(self, file, bot):
        try:
            process = await asyncio.create_subprocess_shell(
                f"mediainfo '''{file}''' --Output=HTML",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            out = stdout.decode()
            client = TelegraphPoster(use_api=True)
            client.create_api_token("Mediainfo")
            page = client.post(
                title="Mediainfo",
                author=((await bot.get_me()).first_name),
                author_url=f"https://t.me/{((await bot.get_me()).username)}",
                text=out,
            )
            return page.get("url")
        except Exception as error:
            LOGS.error(str(error))

    async def _poster(self, bot, anime_info):
        thumb = await self.cover_dl((await anime_info.get_cover()))
        caption = await anime_info.get_caption()
        return await bot.upload_poster(thumb or "assest/poster_not_found.jpg", caption)

    def init_dir(self):
        if not os.path.exists("thumb.jpg"):
            os.system(f"wget {Var.THUMB} -O thumb.jpg")
        if not os.path.isdir("encode/"):
            os.mkdir("encode/")
        if not os.path.isdir("thumbs/"):
            os.mkdir("thumbs/")
        if not os.path.isdir("downloads/"):
            os.mkdir("downloads/")

    def code(self, data):
        OK.update({len(OK): data})
        return str(len(OK) - 1)

    def decode(self, key):
        if OK.get(int(key)):
            return OK[int(key)]
        return

    def hbs(self, size):
        if not size:
            return ""
        power = 2**10
        raised_to_pow = 0
        dict_power_n = {0: "B", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
        while size > power:
            size /= power
            raised_to_pow += 1
        return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"

    async def rename_file(self, dl, out):
        try:
            os.rename(dl, out)
        except BaseException:
            return False, format_exc()
        return True, out

    async def compress(self, dl, out):
        cmd = f'''{Var.FFMPEG} -i """{dl}""" -metadata "Encoded By"="https://github.com/kaif-00z/AutoAnimeBot/" -preset ultrafast -c:v libx265 -crf {Var.CRF} -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? """{out}""" -y'''
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        err = stderr.decode().strip()
        if err:
            return False, err
        return True, out

    async def stats(self, e):
        try:
            wah = e.pattern_match.group(1).decode("UTF-8")
            ah = self.decode(wah)
            out, dl = ah.split(";")
            ot = self.hbs(int(Path(out).stat().st_size))
            ov = self.hbs(int(Path(dl).stat().st_size))
            ans = f"Downloaded:\n{ov}\n\nCompressing:\n{ot}"
            await e.answer(ans, cache_time=0, alert=True)
        except Exception as error:
            await e.answer(f"Someting Went Wrong!\n{error}", cache_time=0, alert=True)

    async def genss(self, file):
        process = subprocess.Popen(
            ["mediainfo", file, "--Output=JSON"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout, stderr = process.communicate()
        out = stdout.decode().strip()
        z = json.loads(out)
        p = z["media"]["track"][0]["Duration"]
        return int(p.split(".")[-2])

    def stdr(self, seconds: int) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if len(str(minutes)) == 1:
            minutes = "0" + str(minutes)
        if len(str(hours)) == 1:
            hours = "0" + str(hours)
        if len(str(seconds)) == 1:
            seconds = "0" + str(seconds)
        dur = (
            ((str(hours) + ":") if hours else "00:")
            + ((str(minutes) + ":") if minutes else "00:")
            + ((str(seconds)) if seconds else "")
        )
        return dur

    async def duration_s(self, file):
        tsec = await self.genss(file)
        x = round(tsec / 5)
        y = round(tsec / 5 + 30)
        pin = self.stdr(x)
        if y < tsec:
            pon = self.stdr(y)
        else:
            pon = self.stdr(tsec)
        return pin, pon

    async def gen_ss_sam(self, _hash, filename):
        try:
            ss_path, sp_path = None, None
            os.mkdir(_hash)
            tsec = await self.genss(filename)
            fps = 10 / tsec
            ncmd = f"ffmpeg -i '{filename}' -vf fps={fps} -vframes 10 '{_hash}/pic%01d.png'"
            process = await asyncio.create_subprocess_shell(
                ncmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            ss, dd = await self.duration_s(filename)
            __ = filename.split(".mkv")[-2]
            out = __ + "_sample.mkv"
            _ncmd = f'ffmpeg -i """{filename}""" -preset ultrafast -ss {ss} -to {dd} -c:v libx265 -crf 27 -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? """{out}""" -y'
            process = await asyncio.create_subprocess_shell(
                _ncmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            er = stderr.decode().strip()
            try:
                if er:
                    if not os.path.exists(out) or os.path.getsize(out) == 0:
                        LOGS.error(str(er))
                        return (ss_path, sp_path)
            except BaseException:
                pass
            return _hash, out
        except Exception as error:
            LOGS.error(str(error))
