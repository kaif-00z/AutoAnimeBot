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
import logging
from traceback import format_exc

from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError

from functions.config import Var

logging.basicConfig(
    format="%(asctime)s || %(name)s [%(levelname)s] : %(message)s",
    handlers=[
        logging.FileHandler("AutoAnimeBot.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
    datefmt="%m/%d/%Y, %H:%M:%S",
)
LOGS = logging.getLogger("AutoAnimeBot")
TelethonLogger = logging.getLogger("Telethon")
TelethonLogger.setLevel(logging.INFO)

LOGS.info(
    """
                        Auto Anime Bot
                ©️ t.me/kAiF_00z (github.com/kaif-00z)
                        v0.0.8 (original)
                             (2023-24)
                       [All Rigth Reserved]

    """
)


class Reporter:
    def __init__(self, client: TelegramClient, file_name: str):
        self.client: TelegramClient = client
        self.file_name = file_name
        self.msg = None

    async def alert_new_file_founded(self):
        await self.awake()
        msg = await self.client.send_message(
            Var.MAIN_CHANNEL if Var.LOG_ON_MAIN else Var.LOG_CHANNEL,
            f"**New Anime Released**\n\n **File Name:** ```{self.file_name}```\n\n**STATUS:** `Downloading...`",
        )
        self.msg = msg

    async def started_compressing(self):
        self.msg = await self.msg.edit(
            f"**Successfully Downloaded The Anime**\n\n **File Name:** ```{self.file_name}```\n\n**STATUS:** `Encoding...`",
        )
        return self.msg

    async def started_renaming(self):
        self.msg = await self.msg.edit(
            f"**Successfully Downloaded The Anime**\n\n **File Name:** ```{self.file_name}```\n\n**STATUS:** `Renaming...`",
        )

    async def started_uploading(self):
        self.msg = await self.msg.edit(
            f"**Successfully Encoded The Anime**\n\n **File Name:** ```{self.file_name}```\n\n**STATUS:** `Uploading...`"
        )

    async def started_gen_ss(self):
        self.msg = await self.msg.edit(
            f"**Successfully Uploaded The Anime**\n\n **File Name:** ```{self.file_name}```\n\n**STATUS:** `Generating Sample And Screen Shot...`"
        )

    async def all_done(self):
        try:
            self.msg = await self.msg.edit(
                f"**Successfully Completed All Task Related To The Anime**\n\n **File Name:** ```{self.file_name}```\n\n**STATUS:** `DONE`"
            )
        except BaseException:
            pass  # ValueError Sometimes From telethon
        if Var.LOG_ON_MAIN:
            await self.msg.delete()

    async def awake(self):  # in case
        if not self.client.is_connected():
            await self.client.connect()

    async def report_error(self, msg, log=False):
        txt = f"[ERROR] {msg}"
        if log:
            LOGS.error(txt[0])
        try:
            await self.client.send_message(Var.LOG_CHANNEL, f"```{txt[:4096]}```")
        except FloodWaitError as fwerr:
            await self.client.disconnect()
            LOGS.info("Sleeping Becoz Of Floodwait...")
            await asyncio.sleep(fwerr.seconds + 10)
            await self.client.connect()
        except ConnectionError:
            await self.client.connect()
        except Exception as err:
            LOGS.exception(format_exc())
            LOGS.error(str(err))
