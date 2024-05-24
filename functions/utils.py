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

from telethon import Button, events

from core.bot import Bot, Var, asyncio
from database import DataBase


class AdminUtils:
    def __init__(self, dB: DataBase, bot: Bot):
        self.db = dB
        self.bot = bot

    def admin_panel(self):
        btn = [
            [
                Button.inline("📜 LOGS", data="slog"),
                Button.inline("♻️ Restart", data="sret"),
            ],
            [
                Button.inline("🎞️ Encode [Toogle]", data="entg"),
            ],
            [Button.inline("🔘 Button Upload [Toogle]", data="butg")],
            [Button.inline("🗃️ Separate Channel Upload [Toogle]", data="scul")],
            [Button.inline("🔊 Broadcast", data="cast")],
        ]
        return btn

    def back_btn(self):
        return [[Button.inline("🔙", data="bek")]]

    async def _logs(self, e):
        await e.delete()
        await e.reply(
            file="AutoAnimeBot.log", thumb="thumb.jpg", buttons=self.back_btn()
        )

    async def _restart(self, e, schedule):
        await e.reply("`Restarting...`")
        schedule.restart()

    async def _encode_t(self, e):
        if self.db.is_original_upload():
            self.db.toggle_original_upload()
            return await e.edit(
                "`Successfully On The Compression`", buttons=self.back_btn()
            )
        self.db.toggle_original_upload()
        return await e.edit(
            "`Successfully Off The Compression`", buttons=self.back_btn()
        )

    async def _btn_t(self, e):
        if self.db.is_separate_channel_upload():
            return await e.edit(
                "`You Can't On/Off The Button Upload When Seprate Channel Is Enabled`",
                buttons=self.back_btn(),
            )
        if self.db.is_button_upload():
            self.db.toggle_button_upload()
            return await e.edit(
                "`Successfully Off The Button Upload`", buttons=self.back_btn()
            )
        self.db.toggle_button_upload()
        return await e.edit("`Successfully On The Upload`", buttons=self.back_btn())

    async def _sep_c_t(self, e):
        if Var.SESSION:
            if self.db.is_button_upload():
                if self.db.is_separate_channel_upload():
                    self.db.toggle_separate_channel_upload()
                    return await e.edit(
                        "`Successfully Off The Separate Channel Upload`",
                        buttons=self.back_btn(),
                    )
                self.db.toggle_separate_channel_upload()
                return await e.edit(
                    "`Successfully On The Separate Channel Upload`",
                    buttons=self.back_btn(),
                )
            else:
                return await e.edit(
                    "`To Use The Separate Channel Upload First You Have To Enable Button Upload`",
                    buttons=self.back_btn(),
                )
        else:
            return await e.edit(
                "`To Use The Separate Channel Upload First You Have To Add SESSION Variable in The Bot",
                buttons=self.back_btn(),
            )

    async def broadcast_bt(self, e):
        users = self.db.get_broadcast_user()
        await e.edit("Please use his feature Responsibly⚠️")
        await e.reply(
            f"**Send a single Message To Broadcast😉**\n\n**There are** `{len(users)}` **Users Currently Using Me👉🏻**.\n\nSend /cancel to Cancel Process."
        )
        async with e.client.conversation(e.sender_id) as cv:
            reply = cv.wait_event(events.NewMessage(from_users=e.sender_id))
            repl = await reply
            await e.delete()
            if repl.text and repl.text.startswith("/cancel"):
                return await repl.reply("`Broadcast Cancelled`")
        sent = await repl.reply("`🗣️ Broadcasting Your Post...`")
        done, er = 0, 0
        for user in users:
            try:
                if repl.poll:
                    await repl.forward_to(int(user))
                else:
                    await e.client.send_message(int(user), repl.message)
                await asyncio.sleep(0.2)
                done += 1
            except BaseException as ex:
                er += 1
                print(ex)
        await sent.edit(
            f"**Broadcast Completed To** `{done}` **Users.**\n**Error in** `{er}` **Users.**"
        )
