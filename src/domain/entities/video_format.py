from pydantic import BaseModel


class VideoFormat(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
