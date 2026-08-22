export interface ICursos {
  id: number;
  url_image: string | null;
  titulo: string;
  id_instrutor: number;
  instrutor: string;
  id_nivel: number;
  nivel: string;
  avaliacao: number;
  quantidade_avaliacoes: number;
  preco: number;
}

export interface ICourseSearchItem extends ICursos {
  descricao: string;
  id_categoria: number;
  categoria: string;
}

export interface ISearchOption {
  id: number;
  label: string;
}

export interface ICourseSearchData {
  items: ICourseSearchItem[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
    has_previous: boolean;
    has_next: boolean;
  };
  facets: {
    categories: ISearchOption[];
    levels: ISearchOption[];
    instructors: ISearchOption[];
  };
}
