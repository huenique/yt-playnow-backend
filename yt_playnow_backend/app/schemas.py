from typing import Optional

from pydantic import BaseModel


class Payload(BaseModel):
    url: str
    term: Optional[str] = None


class File(BaseModel):
    name: str


class FileInResponse(File):
    size: str
