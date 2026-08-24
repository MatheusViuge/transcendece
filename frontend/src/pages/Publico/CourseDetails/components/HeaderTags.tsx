import { FaStar, FaRegClock, FaRegChartBar } from "react-icons/fa";
import { styles } from "./styles";

interface HeaderTagsProps {
  rating: number;
  reviewCount: number;
  durationHours: number;
  difficulty: string;
}

export function HeaderTags({ rating, reviewCount, durationHours, difficulty }: HeaderTagsProps) {
  return (
    <div className={styles.tagsWrapper}>
      <div className="flex items-center gap-1.5">
        <FaStar className={styles.starIcon} />
        <span className="text-base">{rating.toFixed(1)}</span>
        <span className="text-blue-300 font-normal">
          ({reviewCount} {reviewCount === 1 ? "avaliação" : "avaliações"})
        </span>
      </div>

      <div className={styles.tagItem}>
        <FaRegClock className={styles.icon} />
        {durationHours} {durationHours === 1 ? "hora" : "horas"}
      </div>

      <div className={styles.tagItem}>
        <FaRegChartBar className={styles.icon} />
        {difficulty}
      </div>
    </div>
  );
}
