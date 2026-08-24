import { styles } from "./styles";
import { HeaderTags } from "./HeaderTags";
import { HeaderPrice } from "./HeaderPrice";

interface CourseHeaderProps {
  title: string;
  description: string;
  rating: number;
  reviewCount: number;
  durationHours: number;
  difficulty: string;
  price: number;
  instructor: string;
  specialty?: string;
}

export function CourseHeader({
  title,
  description,
  rating,
  reviewCount,
  durationHours,
  difficulty,
  price,
  instructor,
  specialty,
}: CourseHeaderProps) {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{title}</h1>

      <p className={styles.description}>{description}</p>

      <p className="text-sm text-blue-200">
        Instrutor: {instructor}
        {specialty ? ` · ${specialty}` : ""}
      </p>

      <HeaderTags
        rating={rating}
        reviewCount={reviewCount}
        durationHours={durationHours}
        difficulty={difficulty}
      />

      <HeaderPrice price={price} />
    </div>
  );
}
