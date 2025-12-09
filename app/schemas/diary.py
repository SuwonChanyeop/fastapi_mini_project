from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class DiaryBase(BaseModel):
    title: str
    content: str


class DiaryCreate(DiaryBase):
    pass


class DiaryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class DiaryResponse(DiaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class DiaryListResponse(BaseModel):
    items: List[DiaryResponse]
    total: int
