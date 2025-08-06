from pydantic import BaseModel, model_validator, Field
from typing import List, Optional


class CafeBaseSchema(BaseModel):
    title: str
    city: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class CafeCreateSchema(CafeBaseSchema):
    best_for: str
    also_good_for: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def no_duplicate_best_for(self):
        if self.best_for in self.also_good_for:
            raise ValueError(f"Category '{self.best_for}' duplicated in best_for and also_good_for")
        return self


class CafeUpdateSchema(BaseModel):
    title: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    best_for: Optional[str] = None
    also_good_for: Optional[List[str]] = None

    @model_validator(mode='after')
    def no_duplicate_best_for(self):
        if self.best_for and self.also_good_for and self.best_for in self.also_good_for:
            raise ValueError(f"Category '{self.best_for}' duplicated in best_for and also_good_for")
        return self


class CafeResponseSchema(CafeBaseSchema):
    id: int
    image_url: Optional[str] = None
    average_rating: float = 0.0
    best_for: Optional[str] = None
    also_good_for: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def transform_category_objects_to_names(cls, data):
        if not isinstance(data, dict):
            processed_data = {
                'id': getattr(data, 'id', None),
                'title': getattr(data, 'title', None),
                'city': getattr(data, 'city', None),
                'description': getattr(data, 'description', None),
                'image_url': getattr(data, 'image_url', None),
                'average_rating': getattr(data, 'average_rating', 0.0)
            }
            category_associations = getattr(data, 'category_associations', None)
        else:
            processed_data = data.copy()
            category_associations = data.get('category_associations', None)
        best_for_name = None
        also_good_for_names = []
        if category_associations is not None:
            for assoc in category_associations:
                category = getattr(assoc, 'category', None)
                if category and hasattr(category, 'name'):
                    if getattr(assoc, 'is_best', False):
                        best_for_name = category.name
                    else:
                        also_good_for_names.append(category.name)
        processed_data['best_for'] = best_for_name
        processed_data['also_good_for'] = also_good_for_names
        if 'average_rating' not in processed_data:
            processed_data['average_rating'] = 0.0
        return processed_data
