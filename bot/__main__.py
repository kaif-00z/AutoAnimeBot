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

import re
import secrets
import shutil
from glob import glob
from itertools import count
from traceback import format_exc

import feedparser

from qbwarp import download_magnet

from . import *
from .database import (
    append_name_in_memory,
    get_memory,
    get_store_items,
    is_compress,
    store_items,
)
from .dts import shu_msg
from .func import code, cover_dl, gen_ss_sam, mediainfo, run_async, stats
from .rename import _rename, get_caption, get_cover, get_poster


@bot.on(
    events.NewMessage(
        incoming=True, pattern="^/start ?(.*)", func=lambda e: e.is_private
    )
)
async def _start(event):
    msg_id = event.pattern_match.group(1)
    xnx = await event.reply("`Please Wait...`")
    if msg_id:
        if msg_id.isdigit():  # this is diff thing , just ignore it
            msg = await bot.get_messages(Var.MAIN_CHANNEL, ids=int(msg_id))
            await event.reply(msg, buttons=Button.clear())
        else:
            items = get_store_items(msg_id)
            if items:
                for id in items:
                    msg = await bot.get_messages(Var.CLOUD_CHANNEL, ids=id)
                    await event.reply(file=[i for i in msg])
    else:
        await event.reply(
            f"Hi {event.sender.first_name}\n**How Are You?**",
            buttons=[
                [
                    Button.url("Developer", url="t.me/kaif_00z"),
                    Button.url("Repo", url="https://github.com/kaif-00z/AutoAnimeBot/"),
                ]
            ],
        )
    await xnx.delete()


@bot.on(events.NewMessage(incoming=True, pattern="/opt$", func=lambda e: e.is_private))
async def _opt(event):
    if event.sender_id != Var.OWNER:
        return
    if is_compress():
        dB.set("COMPRESS", "False")
        MEM.update({"COMPRESS": False})
        return await event.reply("`Successfully Off The Compression`")
    dB.set("COMPRESS", "True")
    MEM.update({"COMPRESS": True})
    return await event.reply("`Successfully On The Compression`")


@bot.on(events.NewMessage(incoming=True, pattern="/logs$", func=lambda e: e.is_private))
async def _logs(event):
    if event.sender_id != Var.OWNER:
        return
    await event.reply(file="AutoAnimeBot.log", thumb="thumb.jpg")


@bot.on(
    events.NewMessage(incoming=True, pattern="/restart$", func=lambda e: e.is_private)
)
async def _restart(event):
    if event.sender_id != Var.OWNER:
        return
    await event.reply("`Restarting...`")
    os.execl(sys.executable, sys.executable, "-m", "bot", "--samedb")


@bot.on(
    events.NewMessage(incoming=True, pattern="/skipul", func=lambda e: e.is_private)
)
async def _skiped_ul(event):
    if event.sender_id != Var.OWNER:
        return
    try:
        index = int(event.text.split()[1])
    except BaseException:
        index = 1
    if REQUEST:
        return await event.reply(
            "`Already Your 1st Request Is Running!!! So Try Again After Current Request Completed!!!`"
        )
    xx = await event.reply("`Request Added`")
    REQUEST.append(True)
    await asyncio.gather(
        *[
            geter("https://subsplease.org/rss/?r=720", index),
            geter("https://subsplease.org/rss/?r=1080p", index),
        ]
    )
    REQUEST.clear()
    await xx.reply("`Request Completed`")


async def further_work(msg_id, filename, quality):
    try:
        msg = await bot.get_messages(Var.MAIN_CHANNEL, ids=msg_id)
        btn = [
            [],
        ]
        bac_msg = (
            await bot.send_message(Var.BACKUP_CHANNEL, msg)
            if Var.BACKUP_CHANNEL
            else None
        )
        link_info = await mediainfo(filename, bot)
        if link_info:
            btn.append(
                [
                    Button.url(
                        "📜 MediaInfo",
                        url=link_info,
                    )
                ]
            )
            await msg.edit(buttons=btn)
        hash = secrets.token_hex(nbytes=7)
        ss_path, sp_path = await gen_ss_sam(hash, filename, LOGS)
        if ss_path and sp_path:
            ss = await bot.send_message(Var.CLOUD_CHANNEL, file=glob(f"{ss_path}/*"))
            sp = await bot.send_message(
                Var.CLOUD_CHANNEL, file=sp_path, thumb="thumb.jpg", force_document=True
            )
            store_items(hash, [[i.id for i in ss], [sp.id]])
            await reporter.report(
                "Successfully Generated Screen Shot And Sample.", info=True, log=True
            )
            btn.append(
                [
                    Button.url(
                        "📺 Sample & ScreenShots",
                        url=f"https://t.me/{((await bot.get_me()).username)}?start={hash}",
                    )
                ]
            )
            await msg.edit(buttons=btn)
            try:
                await bac_msg.edit(buttons=btn) if Var.BACKUP_CHANNEL else None
                shutil.rmtree(hash)
                os.remove(sp_path)
                os.remove(filename)
            except BaseException:
                LOGS.error(format_exc())
    except Exception as err:
        LOGS.error(str(err))


async def upload(torrent_link, name, compress=False):
    rename = ""
    try:
        await download_magnet(torrent_link, "./Downloads")
        dl = f"""Downloads/{name}"""
        if os.path.exists(dl):
            if compress:
                rename = await _rename(name)
                out = f"""encode/{rename}"""
                _code = code(f"{out};{dl}")
                com_stat = await bot.send_message(
                    Var.LOG_CHANNEL,
                    f"```New File Downloaded, Named {name}\nNow Going To Commpress```",
                    buttons=[[Button.inline("STATS", data=f"tas_{_code}")]],
                )
                cmd = f'''{Var.FFMPEG} -i """{dl}""" -metadata "Encoded By"="t.me/Anime_Flares" -preset ultrafast -c:v libx265 -crf 25 -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? """{out}""" -y'''
                process = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                err = stderr.decode().strip()
                await com_stat.edit(buttons=Button.clear())
                if not os.path.exists(out) or os.path.getsize(out) == 0:
                    await reporter.report(
                        err if err else "Encode Error.", error=True, log=True
                    )
                    return (False, None, None)
                await reporter.report(
                    "Succesfully Compressed Now Going To Upload...", info=True, log=True
                )
            else:
                await reporter.report(
                    "New File Downloaded, Named {}\nNow Going To Upload".format(name),
                    info=True,
                    log=True,
                )
                rename = await _rename(name, og=True)
                out = f"encode/{rename}"
                os.system(f"""cp '''{dl}''' '''{out}'''""")
                await reporter.report(
                    "Successfully Renamed Now Going To Upload...", info=True, log=True
                )
            thumb = await cover_dl((await get_cover(name)))
            if not pyro.is_connected:
                try:
                    await pyro.connect()
                    await asyncio.sleep(8)
                except ConnectionError:
                    pass
            # async with pyro:
            post = await pyro.send_document(
                Var.MAIN_CHANNEL,
                out,
                caption=f"`{rename}`",
                force_document=True,
                thumb=thumb or "thumb.jpg",
            )
            await reporter.report(
                "Succesfully Uploaded New Video.", info=True, log=True
            )
            os.remove(dl)
            return (True, post.id, out)
        LOGS.error("File Not Found!")
        return (False, None, None)
    except Exception as er:
        LOGS.error(format_exc())
        await reporter.report(str(er), error=True, log=True)
        return (False, None, None)


@run_async
def feedp(link, index=0):
    try:
        feed = feedparser.parse(link)
        return feed.entries[index]
    except BaseException:
        return None


async def geter(link, index=0):
    try:
        info = await feedp(link, index)
        if not info:
            return
        name = info.title
        magnet = info.link
        quality = link.split("/?r=")[1]
        if name not in get_memory(quality, from_memory=True):
            if "[Batch]" in name:
                append_name_in_memory(name, quality, in_memory=True)
            else:
                await reporter.report(
                    f"New File Found!\nNamed - {name}", info=True, log=True
                )
                try:
                    if quality == "1080":
                        await asyncio.sleep(10)
                    poster = await get_poster(name)
                    if poster:
                        if (poster.split("/")[-1]) not in POST_TRACKER:
                            thb = await cover_dl(poster)
                        await bot.send_file(
                            Var.MAIN_CHANNEL,
                            file=thb,
                            caption=(await get_caption(name)),
                            parse_mode="HTML",
                        )
                        POST_TRACKER.append(poster.split("/")[-1])
                except BaseException:
                    pass
                res, msg_id, filename = await upload(
                    magnet, name, compress=is_compress(from_memory=True)
                )
                if res:
                    append_name_in_memory(name, quality, in_memory=True)
                    asyncio.create_task(further_work(msg_id, filename, quality))
    except Exception as error:
        LOGS.error(format_exc())
        LOGS.error(str(error))


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("tas_(.*)")))
async def _(e):
    await stats(e)


async def syst(link1, link2):  # work as webhook
    for i in count():
        # await asyncio.gather(*[geter(link1, 1), geter(link2, 1)])
        await asyncio.gather(*[geter(link1), geter(link2)])


sch.add_job(shu_msg, "cron", hour=0, minute=30)  # 12:30 am IST

LOGS.info("Auto Anime Bot Has Started...")

# Scheduler Start
sch.start()

# notify ppl about the repo and dev
bot.loop.run_until_complete(notify_about_me())

# Webhook for upload and other stuffs
try:
    bot.loop.run_until_complete(
        syst("https://subsplease.org/rss/?r=720", "https://subsplease.org/rss/?r=1080")
    )

    # loop
    bot.loop.run_forever()
except KeyboardInterrupt:
    LOGS.info("Stopping The Bot...")
    try:
        [shutil.rmtree(fold) for fold in ["Downloads", "thumbs", "encode"]]
    except BaseException:
        LOGS.error(format_exc())
    exit()
