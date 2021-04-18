import os
from pathlib import Path
from typing import Any

from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch

from .settings import BASE_DIR, MEDIA_ROOT

YOUTUBE_URL = 'https://youtube.com'


class YoutubeDownloadUtil:

    def __init__(self):
        self.dl_name = None
        self.dl_size = None

    def search_video_ytdl(self, search_term_url: str) -> dict[str, Any]:
        """Search method using youtube-dl.

        Returns a dictionary containing info about the given URL, 
        None otherwise.
        """
        search_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        with YoutubeDL(search_options) as ydl:
            try:
                result = ydl.extract_info(search_term_url, download=False)
            except Exception:
                result = None

        return result

    def search_video_ys(self, search_terms: str) -> dict[str, Any]:
        """Search method using youtube-search.

        Returns a dictionary containing the best match for 
        the search term or URL provided, None otherwise.
        """
        if search_terms and (len(search_terms) > 0):
            try:
                query_res = YoutubeSearch(search_terms,
                                          max_results=5).to_dict()[0]
                result = {
                    'title': query_res.get('title'),
                    'url': YOUTUBE_URL + query_res.get('url_suffix')
                }
            except Exception as exception:
                result = exception
        else:
            result = search_terms

        return result

    def download_progess_hook(self, download):
        if download['status'] == 'finished':
            self.dl_size = download['_total_bytes_str']
            self.dl_name = Path(download['filename']).name

    def download_video_ytdl(self, url: str) -> tuple[str]:
        """Accepts a playlist. If the video is inside a playlist, only extract the single.
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
                'bestaudio/best',
            'progress_hooks': [self.download_progess_hook],
        }
        with YoutubeDL(ydl_opts) as ydl:
            _ = ydl.extract_info(url)

        return self.dl_name, self.dl_size


if __name__ == '__main__':
    ydl_util = YoutubeDownloadUtil()
