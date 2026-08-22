from pydantic import BaseModel, ConfigDict


class SearchOption(BaseModel):
    id: int
    label: str


class CourseSearchFacets(BaseModel):
    categories: list[SearchOption]
    levels: list[SearchOption]
    instructors: list[SearchOption]


class CourseSearchItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url_image: str | None = None
    titulo: str
    descricao: str
    id_instrutor: int
    instrutor: str
    id_nivel: int
    nivel: str
    id_categoria: int
    categoria: str
    avaliacao: float = 0.0
    quantidade_avaliacoes: int = 0
    preco: float = 0.0


class PaginationMetadata(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_previous: bool
    has_next: bool


class CourseSearchData(BaseModel):
    items: list[CourseSearchItem]
    pagination: PaginationMetadata
    facets: CourseSearchFacets
