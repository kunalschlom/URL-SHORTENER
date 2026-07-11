from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class URLBase(BaseModel):
    original_url: str = Field(
        ...,
        description="The original long destination URL to be shortened."
    )

class URLCreate(URLBase):
    pass

class URLResponse(URLBase):
    id: UUID
    short_code: str
    created_at: datetime
    click_count: int
    model_config = ConfigDict(from_attributes=True)
