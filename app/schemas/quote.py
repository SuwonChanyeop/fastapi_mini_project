from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class QuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    author: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime


class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    quote_id: int
    created_at: datetime
    quote: QuoteResponse


class BookmarkListResponse(BaseModel):
    items: List[BookmarkResponse]
    total: int
