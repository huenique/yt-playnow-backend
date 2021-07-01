import os

from starlette.background import BackgroundTasks

from .schemas import File
from .settings import BASE_DIR, MEDIA_ROOT
from .utils import YoutubeDownloadUtil


async def file_state(file_name: File, ydl: YoutubeDownloadUtil,
               bg_task: BackgroundTasks) -> str:
    fpath = await path_to_file_exists(file_name)
    await remove_file_from_sys(bg_task, ydl, fpath)
    return fpath


async def path_to_file_exists(file_name: File) -> str:
    fname = str(dict(file_name).get('name'))
    fpath = os.path.join(*f'{BASE_DIR},{MEDIA_ROOT},{fname}'.split(','))
    if not os.path.isfile(fpath):
        raise FileNotFoundError(fname)
    return fpath


async def remove_file_from_sys(bg_task: BackgroundTasks, ydl: YoutubeDownloadUtil,
                         file_path: str) -> None:
    bg_task.add_task(ydl.remove_file, file_path)
