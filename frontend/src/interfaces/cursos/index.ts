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
