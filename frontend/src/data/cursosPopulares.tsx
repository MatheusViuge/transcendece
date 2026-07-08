export interface Curso {
  id: number;
  titulo: string;
  instrutor: string;
  url_image: string;
  avaliacao: number;
  quantidade_avaliacoes: number;
  preco: number; 
}

const cursosPopulares: Curso[] = [
    {
        id: 1,
        titulo: "Bootcamp FullStack Java + React",
        instrutor: "Guilherme Clemente",
        url_image: "https://wordpress-cms-gc-prod-assets.quero.space/uploads/2021/07/Cursos-de-faculdade.jpg",
        avaliacao: 4.8,
        quantidade_avaliacoes: 2341,
        preco: 49.99
    },

    {
        id: 2,
        titulo: "Desenvolvimento Mobile",
        instrutor: "Matheus Viana",
        url_image: "https://www.cursosrapidosgratis.com.br/site/seo/img/cursos-online.jpg",
        avaliacao: 4.7,
        quantidade_avaliacoes: 2094,
        preco: 0

    },

    {
        id: 3,
        titulo: "Python para Iniciantes",
        instrutor: "Caroliny Gonçalves",
        url_image: "https://concursossc.com.br/wp-content/uploads/2023/03/cursos-profissionalizantes-gratuitos.jpg",
        avaliacao: 4.9,
        quantidade_avaliacoes: 3210,
        preco: 59.99
    }

];

export default cursosPopulares;