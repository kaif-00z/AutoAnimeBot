import asyncio


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip() or None
    out = stdout.decode().strip()
    return out, err


async def download_magnet(link: str, path: str):
    cmd = f"""aria2c '''{link}''' -x 10 -j 10 --seed-time=0 -d '{path}'"""
    await bash(cmd)
