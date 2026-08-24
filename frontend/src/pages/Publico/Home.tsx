import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card/index";
import CategoriesGrid from "@/components/Categories/CategoriesGrid";
import { BaseInput } from "@/components/Form";
import Hero from "@/components/Hero";
import { Alert, EmptyState, Spinner } from "@/design-system";
import type { ICursos } from "@/interfaces/cursos";
import { searchSchema, type SearchFormData } from "@/pages/Publico/schemas/searchSchema";
import { api, catchCustom } from "@/services/api";

export default function Home() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<ICursos[]>([]);
  const [coursesLoading, setCoursesLoading] = useState(true);
  const [coursesError, setCoursesError] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SearchFormData>({
    resolver: zodResolver(searchSchema),
    defaultValues: { busca: "" },
  });

  useEffect(() => {
    let active = true;

    api.get<ICursos[]>({
      url: "/courses/",
      hiddenToast: true,
    })
      .then((response) => {
        if (!active) return;
        setCourses(response.data);
      })
      .catch((error) => {
        if (!active) return;
        setCoursesError(true);
        catchCustom(error);
      })
      .finally(() => {
        if (active) setCoursesLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const popularCourses = useMemo(
    () => [...courses]
      .sort((left, right) => {
        if (right.quantidade_avaliacoes !== left.quantidade_avaliacoes) {
          return right.quantidade_avaliacoes - left.quantidade_avaliacoes;
        }
        if (right.avaliacao !== left.avaliacao) {
          return right.avaliacao - left.avaliacao;
        }
        return left.id - right.id;
      })
      .slice(0, 3),
    [courses],
  );

  const onSearch = ({ busca }: SearchFormData) => {
    const params = new URLSearchParams();

    if (busca) params.set("busca", busca);
    const query = params.toString();
    navigate(query ? `/explorar?${query}` : "/explorar");
  };

  return (
    <div className="grid gap-8 pb-12">
      <Hero />

      <form onSubmit={handleSubmit(onSearch)} className="grid xs:inline-flex gap-2 w-full max-w-200 px-4 mx-auto">
        <div className="w-full">
          <BaseInput
            id="buscar"
            placeholder="O que você gostaria de aprender?"
            aria-invalid={Boolean(errors.busca)}
            maxLength={120}
            {...register("busca")}
          />
          {errors.busca && (
            <p className="mt-1 text-xs text-red" role="alert">{errors.busca.message}</p>
          )}
        </div>
        <Button>Buscar</Button>
      </form>

      <section className="px-4 md:px-8 mx-auto w-full max-w-[1300px]">
        <h2 className="text-base font-normal mb-6 text-neutral-900">
          🔥 Cursos Populares
        </h2>

        {coursesLoading ? (
          <div className="grid min-h-44 place-items-center" aria-busy="true">
            <Spinner size="lg" label="Carregando cursos" />
          </div>
        ) : coursesError ? (
          <Alert tone="danger" title="Não foi possível carregar os cursos">
            Tente novamente em alguns instantes.
          </Alert>
        ) : popularCourses.length === 0 ? (
          <EmptyState
            title="Nenhum curso disponível"
            description="Ainda não há cursos cadastrados para exibir como populares."
          />
        ) : (
          <div className="responsive gap-6 animate-fade-in">
            {popularCourses.map((curso) => (
              <Link to={`/cursos/${curso.id}`} key={curso.id}>
                <Card className="transition-all duration-300 hover:-translate-y-1">
                  <Card.Image src={curso.url_image || ""} alt={curso.titulo} />
                  <Card.Body>
                    <Card.Title>{curso.titulo}</Card.Title>
                    <Card.Author>{curso.instrutor}</Card.Author>
                    <Card.Rating rating={curso.avaliacao} reviews={curso.quantidade_avaliacoes} />
                    <Card.Price value={curso.preco} />
                  </Card.Body>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      <CategoriesGrid />
    </div>
  );
}
