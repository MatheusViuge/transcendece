export interface CursoMatriculado {
  id: number;
  titulo: string;
  instrutor: string;
  url_image: string;
  progresso: number;
  progressoTexto: string;
}

export const cursosMatriculados: CursoMatriculado[] = [
  {
    id: 1,
    titulo: "Bootcamp FullStack Java + React",
    instrutor: "Guilherme Clemente",
    url_image: "https://wordpress-cms-gc-prod-assets.quero.space/uploads/2021/07/Cursos-de-faculdade.jpg",
    progresso: 75,
    progressoTexto: "75% Completo"
  },
  {
    id: 2,
    titulo: "Desenvolvimento Mobile",
    instrutor: "Matheus Viana",
    url_image: "https://www.cursosrapidosgratis.com.br/site/seo/img/cursos-online.jpg",
    progresso: 30,
    progressoTexto: "30% Completo"
  },
  {
    id: 3,
    titulo: "Python para Iniciantes",
    instrutor: "Caroliny Gonçalves",
    url_image: "https://concursossc.com.br/wp-content/uploads/2023/03/cursos-profissionalizantes-gratuitos.jpg",
    progresso: 90,
    progressoTexto: "90% Completo"
  }
];