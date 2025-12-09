from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.user import User
from app.models.diary import Diary
from app.models.quote import Quote, QuoteBookmark
