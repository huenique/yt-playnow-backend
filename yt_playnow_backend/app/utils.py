import os
from pathlib import Path

from youtube_dl import YoutubeDL

from .settings import BASE_DIR, MEDIA_ROOT

YOUTUBE_URL = 'https://youtube.com'


class YoutubeDownloadUtil:

    def __init__(self):
        self.dl_name = ''
        self.dl_size = ''

    def remove_file(self, path: str) -> None:
        os.unlink(path)

    def get_youtube_video(self, url: str) -> tuple[str, str]:
        return self._download_video_ydl(url)

    def _download_progess_hook(self, download: dict):
        if download['status'] == 'finished':
            self.dl_size = str(download['_total_bytes_str'])
            self.dl_name = Path(download['filename']).name

    def _download_video_ydl(self, url: str) -> tuple[str, str]:
        """Downloads a Youtube video as an m4a file.
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
            'progress_hooks': [self._download_progess_hook],
        }
        with YoutubeDL(ydl_opts) as ydl:
            _ = ydl.extract_info(url)

        return self.dl_name, self.dl_size


if __name__ == '__main__':
    ydl_util = YoutubeDownloadUtil()
