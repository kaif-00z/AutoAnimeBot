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

import asyncio
import re
import secrets
import shutil
from glob import glob
from itertools import count
from traceback import format_exc

import feedparser

from qbwarp import add_torrent_magnet, delete_torrent_file
from qbwarp.Hash_Fetch import get_hash_magnet

from . import *
from .database import (
    append_name_in_memory,
    get_memory,
    get_store_items,
    is_compress,
    store_items,
)
from .dts import shu_msg
from .func import code, gen_ss_sam, mediainfo, stats
from .google_upload import guploader
from .rename import _rename


@bot.on(
    events.NewMessage(
        incoming=True, pattern="^/start ?(.*)", func=lambda e: e.is_private
    )
)
async def _start(event):
    msg_id = event.pattern_match.group(1)
    xnx = await event.reply("`Please Wait`")
    if msg_id:
        if msg_id.isdigit():
            msg = await bot.get_messages(Var.CHAT, ids=int(msg_id))
            await event.reply(msg, buttons=Button.clear())
        else:
            items = get_store_items(msg_id)
            if items:
                for id in items:
                    msg = await bot.get_messages(Var.CLOUD, ids=id)
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


@bot.on(events.NewMessage(incoming=True, pattern="^/opt$", func=lambda e: e.is_private))
async def _opt(event):
    if str(event.sender_id) not in Var.OWNERS:
        return
    if is_compress():
        dB.set("COMPRESS", "False")
        MEM.update({"COMPRESS": False})
        return await event.reply("`Successfully Off The Compression`")
    dB.set("COMPRESS", "True")
    MEM.update({"COMPRESS": True})
    return await event.reply("`Successfully On The Compression`")


@bot.on(
    events.NewMessage(incoming=True, pattern="^/logs$", func=lambda e: e.is_private)
)
async def _logs(event):
    if str(event.sender_id) not in Var.OWNERS:
        return
    await event.reply(file="AutoAnimeBot.txt", thumb="thumb.jpg")


@bot.on(
    events.NewMessage(incoming=True, pattern="^/skipul", func=lambda e: e.is_private)
)
async def _skiped_ul(event):
    if str(event.sender_id) not in Var.OWNERS:
        return
    try:
        index = int(event.text.split()[1])
    except BaseException:
        index = 1
    xx = await event.reply("`Request Added`")
    await asyncio.gather(
        *[
            geter("https://subsplease.org/rss/?r=720", index),
            geter("https://subsplease.org/rss/?r=1080", index),
        ]
    )
    await xx.edit("`Request Completed")


async def further_work(msg_id, filename, quality):
    try:
        # if quality == "1080":
        #     qued_in = await streamer.add_stream(filename)
        # await reporter.report(f"Added In Queue #{qued_in}", info=True,
        # log=True)
        msg = await bot.get_messages(Var.CHAT, ids=msg_id)
        btn = [
            [
                Button.url(
                    "📲 Send Forwardable Message",
                    url=f"https://t.me/{((await bot.get_me()).username)}?start={msg_id}",
                )
            ],
            [],
        ]
        await msg.edit(buttons=btn)
        bac_msg = await bot.send_message(Var.BACKUP, msg)
        if Var.GDRIVE_UPLOAD:
            await reporter.report("Going To Upload in Gdrive...", info=True, log=True)
            _res, _gid = await guploader(mgauth, Var.GDRIVE_FOLDER_ID, filename, LOGS)
            if _res and _gid:
                btn[1].append(
                    Button.url(
                        "⚡ Index Link",
                        url=f"{Var.INDEX_LINK}{filename.split('/')[-1].strip().replace(' ', '%20')}",
                    )
                )
                btn[0].append(
                    Button.url(
                        "▶️ View Link",
                        url=f"{Var.INDEX_LINK}{filename.split('/')[-1].strip().replace(' ', '%20')}?a=view",
                    )
                )
                btn[1].append(
                    Button.url(
                        "♻️ Gdrive Link",
                        url=f"https://drive.google.com/uc?id={_gid}&export=download",
                    )
                )
                await msg.edit(buttons=btn)
                await reporter.report(
                    "Succesfully Uploaded On Gdrive", info=True, log=True
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
            ss = await bot.send_message(Var.CLOUD, file=glob(f"{ss_path}/*"))
            await asyncio.sleep(2)
            sp = await bot.send_message(Var.CLOUD, file=sp_path, thumb="thumb.jpg")
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
                shutil.rmtree(hash)
                os.remove(sp_path)
            except BaseException:
                pass
        await bac_msg.edit(buttons=btn)
    except Exception as err:
        LOGS.exception(str(err))


async def upload(torrent_link, name, compress=False):
    rename = ""
    try:
        await add_torrent_magnet(torrent_link)
        dl = f"Downloads/{name}"
        if os.path.exists(dl):
            if compress:
                rename = _rename(name)
                out = f"encode/{rename}"
                _code = code(f"{out};{dl}")
                com_stat = await bot.send_message(
                    Var.LOG_CHANNEL,
                    f"```New File Downloaded, Named {name}\nNow Going To Commpress```",
                    buttons=[[Button.inline("STATS", data=f"tas_{_code}")]],
                )
                cmd = f'{Var.FFMPEG} -i "{dl}" -metadata "Encoded By"="github.com/kaif-00z/AutoAnimeBot" -preset ultrafast -c:v libx265 -crf 27 -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? "{out}" -y'
                process = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                err = stderr.decode().strip()
                await com_stat.edit(buttons=Button.clear())
                if not os.path.exists(out) or os.path.getsize(out) == 0:
                    await reporter.report(
                        err[:3250] if err else "Encode Error.", error=True, log=True
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
                rename = _rename(name, og=True)
                out = f"encode/{rename}"
                os.system(f'cp "{dl}" "{out}"')
                await reporter.report(
                    "Successfully Renamed Now Going To Upload...", info=True, log=True
                )
            async with pyro:
                post = await pyro.send_document(
                    Var.CHAT,
                    out,
                    caption=f"`{rename}`",
                    force_document=True,
                    thumb="thumb.jpg",
                    protect_content=True,
                )
            await reporter.report(
                "Succesfully Uploaded New Video.", info=True, log=True
            )
            ext_hash = get_hash_magnet(torrent_link)
            await delete_torrent_file(ext_hash)
            return (True, post.id, out)
        LOGS.error("File Not Found!")
        return (False, None, None)
    except Exception as er:
        LOGS.exception(format_exc())
        await reporter.report(str(er), error=True, log=True)
        return (False, None, None)


async def geter(link, index=0):
    try:
        # asyncio.ensure_future(streamer.start_stream())
        feed = feedparser.parse(link)
        info = feed.entries[index]
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
                if is_compress(from_memory=True):
                    res, msg_id, filename = await upload(magnet, name, compress=True)
                    if res:
                        append_name_in_memory(name, quality, in_memory=True)
                        asyncio.ensure_future(further_work(msg_id, filename, quality))
                else:
                    res, msg_id, filename = await upload(magnet, name)
                    if res:
                        append_name_in_memory(name, quality, in_memory=True)
                        asyncio.ensure_future(further_work(msg_id, filename, quality))
    except Exception as error:
        LOGS.exception(format_exc())
        LOGS.exception(str(error))


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("tas_(.*)")))
async def _(e):
    await stats(e)


async def syst(link1, link2):  # work as webhook
    for i in count():
        # await asyncio.gather(*[geter(link1, 1), geter(link2, 1)]) don't use this line becoz it will blast ur vps
        # await asyncio.gather(*[geter(link1), geter(link2)]) don't use this
        # line becoz it will blast ur vps
        await geter(link1)
        await geter(link2)


sch.add_job(shu_msg, "cron", hour=0, minute=30)  # 12:30 am IST

LOGS.info("Auto Anime Bot Has Started...")

# Scheduler Start
sch.start()

# Streamer Run
# bot.loop.run_until_complete(streamer.run())

# notify ppl about the repo and dev
bot.loop.run_until_complete(notify_about_me())

# Webhook for upload and other stuffs
bot.loop.run_until_complete(
    syst("https://subsplease.org/rss/?r=720", "https://subsplease.org/rss/?r=1080")
)

# loop
bot.loop.run_forever()
