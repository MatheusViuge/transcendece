import { useEffect, useState } from "react";
import { isAxiosError } from "axios";
import { Link, useParams } from "react-router-dom";

import { Alert, EmptyState, Spinner } from "@/design-system";
import type { ICourseDetails } from "@/interfaces/cursos";
import { api, catchCustom } from "@/services/api";
import { CourseHeader } from "./components/CourseHeader";

export default function CourseDetails() {
  const { id } = useParams<{ id: string }>();
  const [course, setCourse] = useState<ICourseDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [requestError, setRequestError] = useState(false);

  useEffect(() => {
    let active = true;
    const courseId = Number(id);

    setCourse(null);
    setNotFound(false);
    setRequestError(false);
    setLoading(true);

    if (!Number.isInteger(courseId) || courseId <= 0) {
      setNotFound(true);
      setLoading(false);
      return () => {
        active = false;
      };
    }

    api.get<ICourseDetails>({
      url: `/courses/${courseId}`,
      hiddenToast: true,
    })
      .then((response) => {
        if (!active) return;
        setCourse(response.data);
      })
      .catch((error) => {
        if (!active) return;

        if (isAxiosError(error) && error.response?.status === 404) {
          setNotFound(true);
          return;
        }

        setRequestError(true);
        catchCustom(error);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [id]);

  if (loading) {
    return (
      <main className="grid min-h-[60vh] place-items-center px-4" aria-busy="true">
        <Spinner size="lg" label="Carregando curso" />
      </main>
    );
  }

  if (notFound) {
    return (
      <main className="grid min-h-[60vh] place-items-center px-4 py-12">
        <EmptyState
          title="Curso não encontrado"
          description="O curso informado não existe ou não está mais disponível."
          action={(
            <Link className="text-primary underline underline-offset-4" to="/explorar">
              Ver cursos disponíveis
            </Link>
          )}
        />
      </main>
    );
  }

  if (requestError || !course) {
    return (
      <main className="mx-auto w-full max-w-3xl px-4 py-12">
        <Alert tone="danger" title="Não foi possível carregar o curso">
          Tente novamente em alguns instantes.
        </Alert>
      </main>
    );
  }

  return (
    <main className="w-full pb-12">
      <CourseHeader
        title={course.titulo}
        description={course.descricao}
        rating={course.avaliacao}
        reviewCount={course.quantidade_avaliacoes}
        durationHours={course.quantidade_horas}
        difficulty={course.nivel}
        price={course.preco}
        instructor={course.instrutor}
        specialty={course.especialidade_instrutor}
      />

      <section className="mx-auto grid w-full max-w-5xl gap-6 px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-xl border border-border bg-surface p-6">
          <h2 className="text-lg font-semibold text-text">Informações do curso</h2>
          <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-text-muted">Instrutor</dt>
              <dd className="font-medium text-text">{course.instrutor}</dd>
            </div>
            <div>
              <dt className="text-text-muted">Especialidade</dt>
              <dd className="font-medium text-text">{course.especialidade_instrutor}</dd>
            </div>
            <div>
              <dt className="text-text-muted">Nível</dt>
              <dd className="font-medium text-text">{course.nivel}</dd>
            </div>
            <div>
              <dt className="text-text-muted">Carga horária</dt>
              <dd className="font-medium text-text">
                {course.quantidade_horas} {course.quantidade_horas === 1 ? "hora" : "horas"}
              </dd>
            </div>
          </dl>
        </div>
      </section>
    </main>
  );
}
