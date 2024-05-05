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
# little bit inspired from pyUltroid.BaseClient

import sys
from logging import Logger

from pyrogram import Client
from telethon import TelegramClient
from telethon.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
)
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

from functions.config import Var
from libs.logger import LOGS, TelethonLogger


class Bot(TelegramClient):
    def __init__(
        self,
        session,
        api_id=None,
        api_hash=None,
        bot_token=None,
        logger: Logger = LOGS,
        log_attempt=True,
        exit_on_error=True,
        *args,
        **kwargs,
    ):
        self._handle_error = exit_on_error
        self._log_at = log_attempt
        self.logger = logger
        kwargs["api_id"] = api_id or Var.API_ID
        kwargs["api_hash"] = api_hash or Var.API_HASH
        kwargs["base_logger"] = TelethonLogger
        super().__init__(session, **kwargs)
        self.pyro_client = Client(
            name="pekka",
            api_id=kwargs["api_id"],
            api_hash=kwargs["api_hash"],
            bot_token=bot_token or Var.BOT_TOKEN,
            in_memory=True,
        )
        self.run_in_loop(self.start_client(bot_token=bot_token or Var.BOT_TOKEN))

    def __repr__(self):
        return "<AutoAnimeBot.Client :\n bot: {}\n>".format(self._bot)

    async def start_client(self, **kwargs):
        """function to start client"""
        if self._log_at:
            self.logger.info("Trying to login.")
        try:
            await self.start(**kwargs)
            await self.pyro_client.start()
        except ApiIdInvalidError:
            self.logger.critical("API ID and API_HASH combination does not match!")
            sys.exit()
        except (AuthKeyDuplicatedError, EOFError):
            if self._handle_error:
                self.logger.critical("String session expired. Create new!")
                return sys.exit()
            self.logger.critical("String session expired.")
        except (AccessTokenExpiredError, AccessTokenInvalidError):
            self.logger.critical(
                "Bot token is expired or invalid. Create new from @Botfather and add in BOT_TOKEN env variable!"
            )
            sys.exit()
        self.me = await self.get_me()
        if self.me.bot:
            me = f"@{self.me.username}"
        if self._log_at:
            self.logger.info(f"Logged in as {me}")
        self._bot = await self.is_bot()

    async def upload_anime(self, file, caption, thumb=None, is_button=False):
        if not self.pyro_client.is_connected:
            try:
                await self.pyro_client.connect()
            except ConnectionError:
                pass
        post = await self.pyro_client.send_document(
            Var.BACKUP_CHANNEL if is_button else Var.MAIN_CHANNEL,
            file,
            caption=f"`{caption}`",
            force_document=True,
            thumb=thumb or "thumb.jpg",
        )
        return post

    async def upload_poster(self, file, caption):
        post = await self.send_file(
            Var.MAIN_CHANNEL,
            file=file,
            caption=caption,
        )
        return post

    async def is_joined(self, channel_id, user_id):
        try:
            await self(GetParticipantRequest(channel=channel_id, participant=user_id))
            return True
        except UserNotParticipantError:
            return False

    def run_in_loop(self, function):
        return self.loop.run_until_complete(function)

    def run(self):
        self.run_until_disconnected()

    def add_handler(self, func, *args, **kwargs):
        if func in [_[0] for _ in self.list_event_handlers()]:
            return
        self.add_event_handler(func, *args, **kwargs)
