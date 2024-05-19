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

import re
from traceback import format_exc

from telethon import Button, events

from core.bot import Bot
from core.executors import Executors
from database import DataBase
from functions.info import AnimeInfo
from functions.schedule import ScheduleTasks, Var
from functions.tools import Tools, asyncio
from functions.utils import AdminUtils
from libs.ariawarp import Torrent
from libs.logger import LOGS, Reporter
from libs.subsplease import SubsPlease

tools = Tools()
tools.init_dir()
bot = Bot(None)
dB = DataBase()
subsplease = SubsPlease(dB)
torrent = Torrent()
schedule = ScheduleTasks(bot)
admin = AdminUtils(dB, bot)


@bot.on(
    events.NewMessage(
        incoming=True, pattern="^/start ?(.*)", func=lambda e: e.is_private
    )
)
async def _start(event):
    msg_id = event.pattern_match.group(1)
    xnx = await event.reply("`Please Wait...`")
    if msg_id:
        if msg_id.isdigit():
            msg = await bot.get_messages(Var.BACKUP_CHANNEL, ids=int(msg_id))
            await event.reply(msg)
        else:
            items = dB.get_store_items(msg_id)
            if items:
                for id in items:
                    msg = await bot.get_messages(Var.CLOUD_CHANNEL, ids=id)
                    await event.reply(file=[i for i in msg])
    else:
        if event.sender_id == Var.OWNER:
            await xnx.delete()
            return await event.reply(
                "** <                ADMIN PANEL                 > **",
                buttons=admin.admin_panel(),
            )
        await event.reply(
            f"**Enjoy Ongoing Anime's Best Encode 24/7 🫡**",
            buttons=[
                [
                    Button.url("👨‍💻 DEV", url="t.me/kaif_00z"),
                    Button.url(
                        "💖 OPEN SOURCE",
                        url="https://github.com/kaif-00z/AutoAnimeBot/",
                    ),
                ]
            ],
        )
    await xnx.delete()


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("tas_(.*)")))
async def _(e):
    await tools.stats(e)


@bot.on(events.callbackquery.CallbackQuery(data="slog"))
async def _(e):
    await admin._logs(e)


@bot.on(events.callbackquery.CallbackQuery(data="sret"))
async def _(e):
    await admin._restart(e, schedule)


@bot.on(events.callbackquery.CallbackQuery(data="entg"))
async def _(e):
    await admin._encode_t(e)


@bot.on(events.callbackquery.CallbackQuery(data="butg"))
async def _(e):
    await admin._btn_t(e)


@bot.on(events.callbackquery.CallbackQuery(data="bek"))
async def _(e):
    await e.edit(buttons=admin.admin_panel())


async def anime(data):
    try:
        torr = [data.get("480p"), data.get("720p"), data.get("1080p")]
        poster = await tools._poster(bot, AnimeInfo(torr[0].title))
        btn = []
        for i in torr:
            try:
                filename = f"downloads/{i.title}"
                reporter = Reporter(bot, i.title)
                await reporter.alert_new_file_founded()
                await torrent.download_magnet(i.link, "./downloads/")
                exe = Executors(
                    bot,
                    dB,
                    {
                        "original_upload": dB.is_original_upload(),
                        "button_upload": dB.is_button_upload(),
                    },
                    filename,
                    AnimeInfo(i.title),
                    reporter,
                )
                result, _btn = await exe.execute()
                if result:
                    if _btn:
                        btn.append(_btn)
                        await poster.edit(buttons=[btn])
                    asyncio.ensure_future(exe.further_work())
                    continue
                await reporter.report_error(_btn, log=True)
            except BaseException:
                await reporter.report_error(str(format_exc()), log=True)
    except BaseException:
        LOGS.error(str(format_exc()))


try:
    bot.loop.run_until_complete(subsplease.on_new_anime(anime))
    bot.run()
except KeyboardInterrupt:
    subsplease._exit()
