from pydantic import BaseModel


class Url(BaseModel):
    url: str


class File(BaseModel):
    name: str


class FileInResponse(File):
    size: str
