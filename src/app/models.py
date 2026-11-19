from pydantic import BaseModel, Field


class Post(BaseModel):
    id: int = Field(gt=0)
    user_id: int = Field(alias="userId", gt=0)
    title: str = Field(min_length=1)
    body: str
