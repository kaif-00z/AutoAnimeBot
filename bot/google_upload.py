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
import json
import multiprocessing
import pickle
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def run_async(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5),
            partial(function, *args, **kwargs),
        )

    return wrapper


def GoogleAuthorizer(name):
    with open(name, "rb") as token:
        credz = pickle.load(token)
    return build("drive", "v3", credentials=credz, cache_discovery=False)


@run_async
def guploader(service, dir_id, filename, log):
    file_metadata = {
        "name": filename.split("/")[-1],
        "description": "Uploaded By github.com/kaif-00z/AutoAnimeBot",
        "mimeType": "video/x-matroska",
        "parents": [dir_id],
    }
    media_body = MediaFileUpload(
        filename,
        mimetype="video/x-matroska",
        resumable=True,
        chunksize=50 * 1024 * 1024,
    )

    drive_file = service.files().create(
        body=file_metadata, media_body=media_body, supportsTeamDrives=True
    )
    response = None

    while response is None:
        try:
            status, response = drive_file.next_chunk()
        except HttpError as err:
            if err.resp.get("content-type", "").startswith("application/json"):
                reason = (
                    json.loads(err.content).get("error").get("errors")[0].get("reason")
                )
                log.exception(str(reason))
                return (False, reason)

    file = service.files().get(fileId=response["id"], supportsTeamDrives=True).execute()

    if file.get("id"):
        return (True, file.get("id"))
    return (False, file.get("id"))
