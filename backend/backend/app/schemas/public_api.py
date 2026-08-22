from datetime import datetime

from pydantic import BaseModel, Field


class PublicReference(BaseModel):
    id: int
    name: str


class PublicCourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    price: float = Field(ge=0)
    workload_hours: int = Field(gt=0, le=10000)
    category_id: int = Field(gt=0)
    level_id: int = Field(gt=0)
    image_url: str | None = Field(default=None, max_length=200)


class PublicCourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    price: float | None = Field(default=None, ge=0)
    workload_hours: int | None = Field(default=None, gt=0, le=10000)
    category_id: int | None = Field(default=None, gt=0)
    level_id: int | None = Field(default=None, gt=0)
    image_url: str | None = Field(default=None, max_length=200)


class PublicCourse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    workload_hours: int
    image_url: str | None
    category: PublicReference
    level: PublicReference
    instructor: PublicReference
    created_at: datetime
    updated_at: datetime


class PublicPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_previous: bool
    has_next: bool


class PublicCoursePage(BaseModel):
    items: list[PublicCourse]
    pagination: PublicPagination
