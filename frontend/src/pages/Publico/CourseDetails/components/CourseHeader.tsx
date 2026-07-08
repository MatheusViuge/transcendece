import { styles } from "./styles";
import { HeaderTags } from "./HeaderTags";
import { HeaderPrice } from "./HeaderPrice";

interface CourseHeaderProps {
  title: string;
  description?: string;
  rating: number;
  studentCount: number;
  duration: number;
  difficulty: string;
  price: number;
}

export function CourseHeader({ 
  title, 
  description = "Aprenda desenvolvimento web do zero com HTML, CSS, JavaScript, React, Node.js e muito mais.",
  rating, 
  studentCount, 
  duration, 
  difficulty, 
  price 
}: CourseHeaderProps) {

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>
        {title}
      </h1>

      <p className={styles.description}>
        {description}
      </p>

      {/* Tags */}
      <HeaderTags 
        rating={rating}
        studentCount={studentCount}
        duration={duration}
        difficulty={difficulty}
      />

      {/* Preço e Botão */}
      <HeaderPrice price={price} />
    </div>
  );
}