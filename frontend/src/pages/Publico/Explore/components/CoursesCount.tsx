interface CoursesCountProps {
  count: number;
}

export default function CoursesCount({ count }: CoursesCountProps) {
  // Se não tiver cursos, a gente não mostra "0 resultados" aqui, 
  // porque o EmptyState já vai cuidar disso visualmente.
  if (count === 0) return null;

  return (
    <div className="animate-fade-in">
      <p className="text text-base">
        {count} cursos encontrados
      </p>
    </div>
  );
}