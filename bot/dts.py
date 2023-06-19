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
# https://github.com/kaif-00z/AutoAnimeBOt/blob/main/LICENSE > .


import json

import aiohttp

from . import POST_TRACKER, Var, bot, reporter
from .rename import get_english


async def shu_msg():
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
        mssg = await bot.send_message(Var.CHAT, text)
        await bot.pin_message(mssg.chat_id, mssg.id, notify=True)
        try:
            POST_TRACKER.clear()
        except BaseException:
            pass
    except Exception as err:
        await reporter.report(str(err), error=True, log=True)
