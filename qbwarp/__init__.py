from torrentp import TorrentDownloader

from bot.func import run_async


@run_async
def download_magnet(link: str, path: str):
    torrent_file = TorrentDownloader(link, path)
    return torrent_file.start_download()
