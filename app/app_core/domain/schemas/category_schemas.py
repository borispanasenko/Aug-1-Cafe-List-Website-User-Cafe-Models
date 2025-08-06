from pydantic import BaseModel, Field


class CategoryCreateSchema(BaseModel):
    name: str = Field(..., max_length=50)


class CategoryResponseSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
        