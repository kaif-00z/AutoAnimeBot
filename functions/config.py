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

from decouple import config


class Var:
    # Telegram Credentials

    API_ID = config("API_ID", default=21310924, cast=int)
    API_HASH = config("API_HASH", default="fa4c3f582286d969ab1d08449e9533e8")
    BOT_TOKEN = config("BOT_TOKEN", default="6830131735:AAFelIqb0CFQjdluupFfpXXpvPSs-HcF9w0")
    FORCESUB_CHANNEL = int("-1001926897432")
    FORCESUB_CHANNEL_2 = int("-1002066884253")
    FORCESUB_CHANNEL_LINK = "https://t.me/Anime_Compass"
    FORCESUB_CHANNEL_LINK_2 = "https://t.me/Ongoing_Compass"
    # Database Credentials

    REDIS_URI = config("REDIS_URI", default="redis-10802.c330.asia-south1-1.gce.redns.redis-cloud.com:10802") 
    REDIS_PASS = config("REDIS_PASSWORD", default="rOvg9VosqTpuE2bcX7sPVDAvuERbezEV")

    # Channels Ids

    BACKUP_CHANNEL = config("BACKUP_CHANNEL", default=-1002106668069, cast=int)
    MAIN_CHANNEL = config("MAIN_CHANNEL", default="-1002066884253", cast=int)
    LOG_CHANNEL = config("LOG_CHANNEL", default="-1002065149795", cast=int)
    CLOUD_CHANNEL = config("CLOUD_CHANNEL", default="-1002065149795", cast=int)
    OWNER = config("OWNER", default="6072442458", cast=int)
    BUTTON_UPLOAD = True 
    # Other Configs 

    THUMB = config(
        "THUMBNAIL", default="https://graph.org/file/4fa004087303b32a4f07d.jpg"
    )
    FFMPEG = config("FFMPEG", default="ffmpeg")
    CRF = config("CRF", default="27")
    SEND_SCHEDULE = config("SEND_SCHEDULE", default=True, cast=bool)
    RESTART_EVERDAY = config("RESTART_EVERDAY", default=False, cast=bool)
