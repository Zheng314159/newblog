from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum
from datetime import datetime
from app.models.user import User  # 确保已导入

class MediaType(str, Enum):
    image = "image"
    video = "video"
    pdf = "pdf"

class MediaFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    type: MediaType
    url: str
    size: int
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    uploader_id: Optional[int] = Field(default=None, foreign_key="user.id")
    uploader: Optional[User] = Relationship(back_populates="media_files")
    # 可选：定义关系
    # uploader: Optional["User"] = Relationship(back_populates="media_files") 