import os

from starlette.background import BackgroundTasks

from .schemas import File
from .settings import BASE_DIR, MEDIA_ROOT
from .utils import YoutubeDownloadUtil


def file_status(file_name: File, ydl: YoutubeDownloadUtil,
                bg_task: BackgroundTasks) -> str:
    fpath = path_to_file_exists(file_name)
    if fpath:
        remove_file_from_sys(bg_task, ydl, fpath)
    return fpath


def path_to_file_exists(file_name: File) -> str:
    exist_path = ''
    fname = str(dict(file_name).get('name'))
    fpath = os.path.join(*f'{BASE_DIR},{MEDIA_ROOT},{fname}'.split(','))
    if os.path.isfile(fpath):
        exist_path = fpath
    return exist_path


def remove_file_from_sys(bg_task: BackgroundTasks, ydl: YoutubeDownloadUtil,
                         file_path: str) -> None:
    bg_task.add_task(ydl.remove_file, file_path)
