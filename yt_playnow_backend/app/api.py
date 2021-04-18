import os
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydub import AudioSegment
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.background import BackgroundTasks
from starlette.requests import Request

from .schemas import File, FileInResponse, Url
from .settings import BASE_DIR, MEDIA_ROOT, ORIGINS
from .utils import YoutubeDownloadUtil

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title='yt-playnow-backend',
    description='Backend logic implementation for yt-playnow',
    version='1.0',
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def _remove_file(path: str) -> None:
    os.unlink(path)


def _fetch_video(url: str) -> tuple[str]:
    with ThreadPoolExecutor() as executor:
        future = executor.submit(YoutubeDownloadUtil().download_video_ytdl, url)
        return future.result()


@app.post('/download')
@limiter.limit("5/minute")
async def download_file(file_name: File, request: Request,
                        background_tasks: BackgroundTasks) -> FileResponse:
    file_name = str(dict(file_name).get('name')) + '.mp3'
    fpath = os.path.join(*f'{BASE_DIR},{MEDIA_ROOT},{file_name}'.split(','))
    if os.path.isfile(fpath):
        background_tasks.add_task(_remove_file, fpath)
        return FileResponse(fpath)
    raise HTTPException(status_code=400)


@app.post('/convert')
@limiter.limit("5/minute")
async def convert_file(file_name: File, request: Request,
                       background_tasks: BackgroundTasks):
    old_fname = dict(file_name).get('name')
    old_fpath = os.path.join(
        *f'{BASE_DIR},{MEDIA_ROOT},{old_fname}.webm'.split(','))
    new_fname = f'{old_fname}.mp3'
    new_fpath = old_fpath.replace('.webm', '.mp3')

    if not os.path.exists(new_fpath):
        if os.path.exists(old_fpath):
            try:
                song = AudioSegment.from_file(old_fpath, 'webm')
                song.export(new_fpath, format='mp3')
                background_tasks.add_task(_remove_file, old_fpath)
                return new_fname
            except Exception as exception:
                raise HTTPException(status_code=400, detail=exception)
        raise HTTPException(status_code=400)

    background_tasks.add_task(_remove_file, old_fpath)
    return new_fname


@app.post('/fetch', response_model=FileInResponse)
@limiter.limit("5/minute")
async def fetch_file(url: Url, request: Request) -> FileInResponse:
    try:
        name, size = _fetch_video(dict(url).get('url'))
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))

    return FileInResponse(name=name.replace('.webm', ''), size=size)
