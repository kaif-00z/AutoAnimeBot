#    This file is part of the AutoAnime distribution.
#    Copyright (c) 2026 Kaif_00z
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
import re
import time

from telethon.errors.rpcerrorlist import MessageNotModifiedError

from libs.logger import LOGS


class Torrent:
    def __init__(self) -> None:
        self.cmd = """aria2c '''{link}''' -x 10 -j 10 --seed-time=0 --summary-interval=1 --show-console-readout=false -d '{path}'"""

    async def bash(self, cmd, reporter=None):
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        last_update = 0

        while True:
            line_bytes = await process.stdout.readline()
            if not line_bytes:
                break
            line = line_bytes.decode(errors="ignore").strip()

            if reporter and ("SPD:" in line or "DL:" in line):
                now = time.time()
                if now - last_update >= 8:
                    per_match = re.search(r"\((\d+)%\)", line)
                    size_match = re.search(r"([\d\.]+\w+)\s*/\s*([\d\.]+\w+)", line)
                    speed_match = re.search(r"(?:SPD:|DL:)\s*([\d\.]+\w+(?:/s)?)", line)
                    eta_match = re.search(r"ETA:([^\s\]]+)", line)

                    spd = re.search(r"SPD:([\d\.]+\w+)", line)
                    dl = re.search(r"DL:([\d\.]+\w+)", line)

                    per = int(per_match.group(1)) if per_match else 0
                    if size_match:
                        size_info = f"{
                            size_match.group(1)} / {
                            size_match.group(2)}"
                    else:
                        size_info = "Unknown"
                    speed_info = (
                        spd.group(1) if spd else (dl.group(1) if dl else "0B/s")
                    )
                    if not speed_info.endswith("/s"):
                        speed_info += "/s"
                    eta_info = eta_match.group(1) if eta_match else "∞"

                    blocks = per // 5
                    progress_bar = "`[{0}{1}] {2}%\n\n`".format(
                        "●" * blocks, " " * (20 - blocks), per
                    )

                    text = (
                        "**📥 Downloading Anime...**\n\n"
                        f"**Name:** `{reporter.file_name}`\n"
                        f"**Size:** `{size_info}`\n"
                        f"**Speed:** `{speed_info}`\n"
                        f"**ETA:** `{eta_info}`\n\n"
                        f"**Progress:**\n{progress_bar}"
                    )

                    try:
                        if hasattr(reporter, "msg"):
                            if reporter.msg:
                                await reporter.msg.edit(
                                    text, buttons=reporter.get_buttons()
                                )
                        else:
                            await reporter.edit(text)
                    except MessageNotModifiedError:
                        pass
                    except Exception as e_edit:
                        LOGS.error(f"Aria progress edit failed: {e_edit}")

                    last_update = now

        await process.wait()
        return "", None

    async def download_magnet(self, link: str, path: str, reporter=None):
        await self.bash(self.cmd.format(link=link, path=path), reporter)
