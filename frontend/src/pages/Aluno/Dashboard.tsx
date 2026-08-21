import { cursosMatriculados } from "@/data/cursosMatriculados";
import { Card } from "@/components/Card/index";
import { Button } from "@/components/Button";
import { useUser } from "@/hooks/useUser";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const { user } = useUser();

  return (
    <div>
      <section className="mx-auto w-full max-w-[1300px] px-4 py-8 md:px-8 md:py-12">
        <h1 className="text-2xl font-normal text-neutral-900">
          Oi, {user?.nome}!
        </h1>
        <p className="mt-2 mb-8 text-neutral-600">Continue com sua jornada de aprendizado!</p>

        <div className="grid min-w-0 grid-cols-1 gap-6 animate-fade-in sm:grid-cols-2 xl:grid-cols-3">
          {cursosMatriculados.map((curso) => (
            <Link key={curso.id} to={`/aluno/cursos/${curso.id}`} className="min-w-0">
              <Card className="h-full min-w-0 transition-all duration-300 hover:-translate-y-1">
                <Card.Image src={curso.url_image} alt={curso.titulo} />
                <Card.Body>
                  <Card.Title>{curso.titulo}</Card.Title>
                  <Card.Author>{curso.instrutor}</Card.Author>
                  <Card.Progress progress={curso.progresso} progressText={curso.progressoTexto} />
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
