import { CourseTabs } from "./components/CourseContent";
import { CourseHeader } from "./components/CourseHeader";

export default function CourseDetails() {
    const cursoTeste = {
        title: "Bootcamp Fullstack Java + React",
        rating: 4.8,
        studentCount: 1240,
        duration: 2700,
        difficulty: "Intermediário",
        price: 199.90
    };

    return (
        <div className="w-full">
            <CourseHeader 
                title={cursoTeste.title}
                rating={cursoTeste.rating}
                studentCount={cursoTeste.studentCount}
                duration={cursoTeste.duration}
                difficulty={cursoTeste.difficulty}
                price={cursoTeste.price}
            />
            
            <div className="w-full max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col w-full max-w-[955px] gap-[32px] pl-[59px] min-h-[372px] py-8">
                    <CourseTabs/>
                </div>
            </div>
        </div>
    );
}