import { cursosMatriculados } from "@/data/cursosMatriculados";
import { Card } from "@/components/Card/index";
import { Button } from "@/components/Button";
import { useUser } from "@/hooks/useUser";
import { api, catchCustom } from "@/services/api";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [matriculas, setMatriculas] = useState();
  const { user } = useUser();

  const buscarMatriculas = async () => {
    try {
        const response = await api.get({ url: `/enrollments`, hiddenToast: true });
        setMatriculas(response.data);
    } catch (error) {
        catchCustom(error);
    }
  };

  useEffect(() => {
    buscarMatriculas();
  }, []);
  console.log(matriculas);

  return (
    <div>
        <section className="py-12 px-4 md:px-8 mx-auto max-w-[1300px]">
            <h1 className="text-2xl font-normal text-neutral-900">
                Oi, {user?.nome}!
            </h1>
            <p className="text-neutral-600 mt-2 mb-8">Continue com sua jornada de aprendizado!</p>

            <div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-6 animate-fade-in">
                { cursosMatriculados.map((curso) =>(
                    <Link to={`/aluno/cursos/${curso.id}`}>
                        <Card key={curso.id} className="transition-all duration-300 hover:-translate-y-1">
                            <Card.Image src={curso.url_image} alt={curso.titulo} />
                            <Card.Body>
                                <Card.Title>{curso.titulo}</Card.Title>
                                <Card.Author>{curso.instrutor}</Card.Author>
                                <Card.Progress progress={curso.progresso} progressText={curso.progressoTexto}></Card.Progress>
                                <Button variant="primary" fullWidth className="mt-4">
                                    Continue Aprendendo
                                </Button>
                            </Card.Body>
                        </Card>
                    </Link>
                ))}
            </div>

        </section>
        
      
    </div>
  );
}