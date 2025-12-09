from pydantic import BaseModel

class QuestionBase(BaseModel):
    question: str

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int

    class Config:
        from_attributes = True
