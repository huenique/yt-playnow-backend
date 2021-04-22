import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

ydl = YoutubeDownloadUtil()


@app.post('/download')
@limiter.limit("5/minute")
async def download_file(file_name: File, request: Request,
                        background_tasks: BackgroundTasks) -> FileResponse:
    file_name = str(dict(file_name).get('name'))
    fpath = os.path.join(*f'{BASE_DIR},{MEDIA_ROOT},{file_name}'.split(','))
    if os.path.isfile(fpath):
        background_tasks.add_task(ydl.remove_file, fpath)
        return FileResponse(fpath)
    raise HTTPException(status_code=400)


@app.post('/collect', response_model=FileInResponse)
@limiter.limit("5/minute")
async def collect_file(url: Url, request: Request) -> FileInResponse:
    try:
        name, size = ydl.get_youtube_video(dict(url).get('url'))
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))
    return FileInResponse(name=name, size=size)
