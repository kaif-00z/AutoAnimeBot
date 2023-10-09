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


import json

import aiohttp

from . import POST_TRACKER, Var, bot, os, reporter, sys
from .rename import get_english


async def shu_msg():
    if Var.SEND_SCHEDULE:
        try:
            async with aiohttp.ClientSession() as ses:
                res = await ses.get(
                    "https://subsplease.org/api/?f=schedule&h=true&tz=Asia/Kolkata"
                )
                _res = await res.text()
            xx = json.loads(_res)
            xxx = xx["schedule"]
            text = "**📆 Anime AirTime Today** `[IST]`\n\n"
            for i in xxx:
                text += f'`[{i["time"]}]` -  [{(await get_english(i["title"]))}](https://subsplease.org/shows/{i["page"]})\n'
            mssg = await bot.send_message(Var.MAIN_CHANNEL, text)
            await bot.pin_message(mssg.MAIN_CHANNEL_id, mssg.id, notify=True)
        except Exception as err:
            await reporter.report(str(err), error=True, log=True)
    POST_TRACKER.clear()
    if Var.RESTART_EVERDAY:
        os.execl(sys.executable, sys.executable, "-m", "bot", "--samedb", "--no-notify")
