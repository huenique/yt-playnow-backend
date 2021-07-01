import asyncio
import os
from pathlib import Path
from typing import Any, Union

from youtube_dl import YoutubeDL

from .settings import BASE_DIR, MEDIA_ROOT

YOUTUBE_URL = 'https://youtube.com'


class YoutubeDownloadUtil:

    def __init__(self):
        self.dl_name = ''
        self.dl_size = ''
        self.loop = asyncio.get_event_loop()

    async def search_video(self, url: str) -> str:
        res = await self.loop.run_in_executor(None, self._sh_video_ydl, url)
        return str(res.get('title', ''))

    async def save_video(self, url: str) -> tuple[str, str]:
        res = await self.loop.run_in_executor(None, self._dl_video_ydl, url)
        return res

    def _sh_video_ydl(self, url: str) -> Union[dict[str, Any], Any, None]:
        search_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        with YoutubeDL(search_options) as ydl:
            return ydl.extract_info(url, download=False)

    def _dl_progess_hook(self, download: dict):
        if download['status'] == 'finished':
            self.dl_size = str(download['_total_bytes_str'])
            self.dl_name = Path(download['filename']).name

    def _dl_video_ydl(self, url: str) -> tuple[str, str]:
        """Download Youtube video as an m4a file.
        """

        # Remove everything after the first occurrence
        # of the separator (&) in the URL.
        if '&list=' in url:
            url = '&'.join(url.split('&')[:1])
        ydl_opts = {
            'quiet':
                True,
            'no_warnings':
                True,
            'outtmpl':
                os.path.join(
                    *f'{BASE_DIR},{MEDIA_ROOT},%(title)s.%(ext)s'.split(',')),
            'format':
                'bestaudio[ext=m4a]',
            'progress_hooks': [self._dl_progess_hook],
        }
        with YoutubeDL(ydl_opts) as ydl:
            _ = ydl.extract_info(url)

        return self.dl_name, self.dl_size
