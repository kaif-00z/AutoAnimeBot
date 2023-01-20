import json

import aiohttp

from . import Var, bot, reporter
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
            text += f'`[{i["time"]}]` -  [{get_english(i["title"])}](https://subsplease.org/shows/{i["page"]})\n'
        mssg = await bot.send_message(Var.CHAT, text)
        await bot.pin_message(mssg.chat_id, mssg.id, notify=True)
    except Exception as err:
        await reporter.report(str(err), error=True, log=True)
