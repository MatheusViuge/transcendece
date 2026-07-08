import { Link } from "react-router-dom";
import { Card } from "@/components/Card"; 
import type { ICursos } from "@/interfaces/cursos";

interface CoursesGridProps {
  courses: ICursos[];
}

export default function CoursesGrid({ courses }: CoursesGridProps) {
  return (
    <div className="responsive gap-6 animate-fade-in">
      {courses.map((course) => (
        <Link key={course.id} to={`/cursos/${course.id}`} className="group">
          <Card 
            className="h-full transition-all duration-300 hover:-translate-y-1"
          >
            <Card.Image src={course.url_image||""} alt={course.titulo} />
            <Card.Body>
              <Card.Title>{course.titulo}</Card.Title>
              <Card.Author>{course.instrutor}</Card.Author>
              <Card.Rating rating={course.avaliacao} reviews={course.quantidade_avaliacoes} />
              <Card.Price value={course.preco} />
            </Card.Body>
          </Card>
        </Link>
      ))}
    </div>
  );
}