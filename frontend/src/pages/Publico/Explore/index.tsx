import CoursesCount from "./components/CoursesCount";
import CoursesGrid from "./components/CoursesGrid";
import EmptyState from "./components/EmptyState";
import { BaseInput } from "@/components/Form";
import { api, catchCustom } from "@/services/api";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSearchParams } from "react-router-dom";
import type { ICursos } from "@/interfaces/cursos";
import { searchSchema, type SearchFormData } from "@/pages/Publico/schemas/searchSchema";

export default function Explore() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [cursos, setCursos] = useState<ICursos[]>([]);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SearchFormData>({
    resolver: zodResolver(searchSchema),
    defaultValues: { busca: searchParams.get("busca") ?? "" },
  });

  useEffect(() => {
    let active = true;

    api.get<ICursos[]>({ url: "/courses/", hiddenToast: true })
      .then((response) => {
        if (active) setCursos(response.data);
      })
      .catch((error) => {
        if (active) catchCustom(error);
      });

    return () => {
      active = false;
    };
  }, []);

  const onSearch = ({ busca }: SearchFormData) => {
    const nextParams = new URLSearchParams(searchParams);

    if (busca) nextParams.set("busca", busca);
    else nextParams.delete("busca");

    setSearchParams(nextParams);
  };

  const query = (searchParams.get("busca") ?? "").trim().toLocaleLowerCase("pt-BR");
  const visibleCourses = query
    ? cursos.filter((course) =>
        [course.titulo, course.instrutor]
          .filter(Boolean)
          .some((value) => value.toLocaleLowerCase("pt-BR").includes(query)),
      )
    : cursos;

  return (
    <div className="grid md:grid-cols-[25rem_1fr] gap-8 w-full mx-auto py-8 px-2 xs:px-16">
      <form onSubmit={handleSubmit(onSearch)} className="col-span-full grid w-full max-w-2xl gap-1">
        <BaseInput
          id="buscar"
          placeholder="Buscar cursos..."
          maxLength={120}
          aria-invalid={Boolean(errors.busca)}
          {...register("busca")}
        />
        {errors.busca && (
          <p className="text-xs text-red" role="alert">{errors.busca.message}</p>
        )}
      </form>

      <section className="w-full" />

      <div>
        {visibleCourses.length > 0 ? (
          <>
            <CoursesCount count={visibleCourses.length} />
            <CoursesGrid courses={visibleCourses} />
          </>
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  );
}
