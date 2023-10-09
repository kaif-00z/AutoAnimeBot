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

from . import MEM, dB


def get_memory(quality, from_memory=False):
    if from_memory:
        return MEM.get(f"MEM_{quality}") or []
    return eval(dB.get(f"MEM_{quality}") or "[]")


def append_name_in_memory(name, quality, in_memory=False):
    if in_memory:
        _data = get_memory(quality, from_memory=True)
        if name not in _data:
            _data.append(name)
            MEM.update({f"MEM_{quality}": _data})
    data = get_memory(quality)
    if name not in data:
        data.append(name)
        dB.set(f"MEM_{quality}", str(data))


def is_compress(from_memory=False):
    if from_memory:
        if MEM.get("COMPRESS") is None:
            return True
        return MEM.get("COMPRESS")
    d = eval(dB.get("COMPRESS") or "None")
    if d is None:
        return True
    return d


def store_items(hash, list):
    data = eval(dB.get("STORE") or "{}")
    data.update({hash: list})
    dB.set("STORE", str(data))


def get_store_items(hash):
    data = eval(dB.get("STORE") or "{}")
    if data.get(hash):
        return data[hash]
    return []
