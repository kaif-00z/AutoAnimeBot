# -*- coding: utf-8 -*-
# (c) YashDK [yash-dk@github]
# (c) modified by AmirulAndalib [amirulandalib@github]

import asyncio as aio
import logging
import os
import time
import traceback
from datetime import datetime
from functools import partial
from random import randint

import aiohttp
import qbittorrentapi as qba
from telethon import events
from telethon.errors.rpcerrorlist import FloodWaitError, MessageNotModifiedError
from telethon.tl.types import KeyboardButtonCallback, KeyboardButtonUrl

from .Hash_Fetch import get_hash_magnet

# logging.basicConfig(level=logging.DEBUG)
torlog = logging.getLogger(__name__)
aloop = aio.get_event_loop()
logging.getLogger("qbittorrentapi").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


async def get_client(
    host=None, port=None, uname=None, passw=None, retry=2
) -> qba.TorrentsAPIMixIn:
    """Creats and returns a client to communicate with qBittorrent server. Max Retries 2"""
    # getting the conn
    host = host if host is not None else "localhost"
    port = port if port is not None else "8090"
    uname = uname if uname is not None else "admin"
    passw = passw if passw is not None else "adminadmin"
    torlog.info(
        f"Trying to login in qBittorrent using creds {host} {port} {uname} {passw}"
    )

    client = qba.Client(host=host, port=port, username=uname, password=passw)

    # try to connect to the server :)
    try:
        await aloop.run_in_executor(None, client.auth_log_in)
        torlog.info("Client connected successfully to the torrent server. 😎")
        return client
    except qba.LoginFailed as e:
        torlog.error(
            "An errot occured invalid creds detected\n{}\n{}".format(
                e, traceback.format_exc()
            )
        )
        return None
    except qba.APIConnectionError:
        if retry == 0:
            torlog.error("Tried to get the client 3 times no luck")
            return None

        torlog.info(
            "Oddly enough the qbittorrent server is not running.... Attempting to start at port {}".format(
                port
            )
        )
        cmd = f"qbittorrent-nox -d --webui-port={port} --profile=."
        cmd = cmd.split(" ")

        subpr = await aio.create_subprocess_exec(
            *cmd, stderr=aio.subprocess.PIPE, stdout=aio.subprocess.PIPE
        )
        _, _ = await subpr.communicate()
        return await get_client(host, port, uname, passw, retry=retry - 1)

async def get_torrent_info(client, ehash=None):

    if ehash is None:
        return await aloop.run_in_executor(None, client.torrents_info)
    else:
        return await aloop.run_in_executor(
            None, partial(client.torrents_info, torrent_hashes=ehash)
        )

async def add_torrent_magnet(magnet):
    """Adds a torrent by its magnet link."""
    client = await get_client()
    try:
        len(await get_torrent_info(client))

        ext_hash = get_hash_magnet(magnet)
        ext_res = await get_torrent_info(client, ext_hash)

        if len(ext_res) > 0:
            torlog.info(f"This torrent is in list {ext_res} {magnet} {ext_hash}")
            return False
        # hot fix for the below issue
        savepath = os.path.join(os.getcwd(), "Downloads")
        # op = await aloop.run_in_executor(
        # None, partial(client.torrents_add, magnet, save_path=savepath)
        # )

        op = client.torrents_add(magnet, save_path=savepath)

        # torrents_add method dosent return anything so have to work around
        if op.lower() == "ok.":
            st = datetime.now()

            ext_res = await get_torrent_info(client, ext_hash)
            if len(ext_res) > 0:
                torlog.info("Got torrent info from ext hash.")
                return ext_res[0]

            while True:
                if (datetime.now() - st).seconds >= 10:
                    torlog.warning(
                        "The provided torrent was not added and it was timed out. magnet was:- {}".format(
                            magnet
                        )
                    )
                    torlog.error(ext_hash)
                    return False
                # commenting in favour of wrong torrent getting returned
                # ctor_new = client.torrents_info()
                # if len(ctor_new) > ctor:
                #    # https://t.me/c/1439207386/2977 below line is for this
                #    torlog.info(ctor_new)
                #    torlog.info(magnet)
                #    return ctor_new[0]
                ext_res = await get_torrent_info(client, ext_hash)
                if len(ext_res) > 0:
                    torlog.info("Got torrent info from ext hash.")
                    return ext_res[0]

        else:
            await torlog.info("This is an unsupported/invalid link.")
    except qba.UnsupportedMediaType415Error as e:
        # will not be used ever ;)
        torlog.error("Unsupported file was detected in the magnet here")
        return False
    except Exception as e:
        torlog.error("{}\n{}".format(e, traceback.format_exc()))
        return False


async def delete_all_torrent():
    client = await get_client()
    tors = await get_torrent_info(client)
    msg = "☠️ Deleted <b>{}</b> torrents.☠️".format(len(tors))
    client.torrents_delete(delete_files=True, torrent_hashes="all")
    torlog.info(msg)


async def delete_torrent_file(ext_hash):
    client = await get_client()
    await aloop.run_in_executor(
        None,
        partial(client.torrents_delete, delete_files=True, torrent_hashes=ext_hash),
    )
    torlog.info("Succesfully Deleted The Following Torrent File")
    return True
