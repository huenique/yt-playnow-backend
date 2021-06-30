import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.background import BackgroundTasks
from starlette.requests import Request

from .helpers import file_status
from .schemas import File, FileInResponse, Url
from .settings import ORIGINS
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
    return FileResponse(file_status(file_name, ydl, background_tasks))


@app.post('/collect', response_model=FileInResponse)
@limiter.limit("5/minute")
async def collect_file(url: Url, request: Request) -> FileInResponse:
    try:
        name, size = ydl.get_youtube_video(str(dict(url).get('url')))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return FileInResponse(name=name, size=size)
