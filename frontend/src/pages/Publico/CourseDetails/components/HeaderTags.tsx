import { FaStar, FaRegClock, FaRegChartBar } from "react-icons/fa";
import { FiUsers } from "react-icons/fi";
import { styles } from "./styles";

interface HeaderTagsProps {
  rating: number;
  studentCount: number;
  duration: number;
  difficulty: string;
}

export function HeaderTags({ rating, studentCount, duration, difficulty }: HeaderTagsProps) {
  return (
    <div className={styles.tagsWrapper}>
      {/* Avaliação */}
      <div className="flex items-center gap-1.5">
        <FaStar className={styles.starIcon} />
        <span className="text-base">{rating}</span> 
        <span className="text-blue-300 font-normal">({studentCount} avaliações)</span>
      </div>
      
      {/* Alunos */}
      <div className={styles.tagItem}>
         <FiUsers className={styles.icon} />
         {studentCount} estudantes
      </div>

      {/* Duração */}
      <div className={styles.tagItem}>
         <FaRegClock className={styles.icon} />
         {(duration / 60).toFixed(0)} horas
      </div>

      {/* Dificuldade */}
      <div className={styles.tagItem}>
         <FaRegChartBar className={styles.icon} />
         {difficulty}
      </div>
    </div>
  );
}