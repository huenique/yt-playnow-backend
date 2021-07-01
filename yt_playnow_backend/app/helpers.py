import os

import youtube_dl
from starlette.background import BackgroundTasks

from .schemas import File
from .settings import BASE_DIR, MEDIA_ROOT
from .utils import YoutubeDownloadUtil


async def file_state(file_name: File, ydl: YoutubeDownloadUtil,
                     bg_task: BackgroundTasks) -> str:
    fpath = await path_to_file(file_name)
    await remove_file_from_sys(fpath, bg_task, ydl)
    return fpath


async def path_to_file(file_name: File) -> str:
    fname = str(dict(file_name).get('name'))
    fpath = os.path.join(*f'{BASE_DIR},{MEDIA_ROOT},{fname}'.split(','))
    if not os.path.isfile(fpath):
        raise FileNotFoundError(fname)
    return fpath


async def remove_file_from_sys(file_path: str,
                               bg_task: BackgroundTasks) -> None:
    bg_task.add_task(os.unlink, file_path)


async def is_supported(url: str) -> bool:
    extors = youtube_dl.extractor.gen_extractors()
    for e in extors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False
