import { basedPathProtected } from "@/pages/Layout/PrivateRoute";
import { useState } from "react";
import { FaChevronDown, FaChevronUp, FaPlayCircle, FaLock } from "react-icons/fa";
import { Link, useLocation } from "react-router-dom";

// Mock de dados (Simulando o Backend)
const modulesMock = [
  {
    id: 1,
    title: "Introdução ao Desenvolvimento Web",
    duration: "2h 30m",
    lessons: [
      { id: 101, title: "Boas vindas e configuração do ambiente", duration: "15:00", isFree: true },
      { id: 102, title: "Como a web funciona?", duration: "25:00", isFree: true },
      { id: 103, title: "Instalando o VS Code", duration: "10:00", isFree: false },
    ]
  },
  {
    id: 2,
    title: "Dominando o HTML5",
    duration: "4h 15m",
    lessons: [
      { id: 201, title: "Estrutura básica do HTML", duration: "20:00", isFree: false },
      { id: 202, title: "Tags semânticas", duration: "30:00", isFree: false },
      { id: 203, title: "Formulários avançados", duration: "45:00", isFree: false },
    ]
  },
  {
    id: 3,
    title: "CSS3: Estilizando a Web",
    duration: "5h 00m",
    lessons: [
      { id: 301, title: "Seletores e cascata", duration: "20:00", isFree: false },
      { id: 302, title: "Flexbox na prática", duration: "40:00", isFree: false },
    ]
  }
];

export function ContentTab() {
  const location = useLocation();
  const isProtectedRoute = basedPathProtected.some(path => location.pathname.startsWith(path));

  // Começamos com o módulo 1 aberto para o usuário ver que é clicável
  const [openModules, setOpenModules] = useState<number[]>([1]);

  const toggleModule = (id: number) => {
    setOpenModules((prev) => 
      prev.includes(id) 
        ? prev.filter((moduleId) => moduleId !== id) // Fecha
        : [...prev, id] // Abre
    );
  };

  return (
    <div className="flex flex-col gap-6 py-6 max-w-4xl text-neutral-800">
      
      {/* 1. Totalizadores (Texto cinza acima da lista) */}
      <div className="flex items-center gap-2 text-sm text-neutral-500 font-normal">
        <span>{modulesMock.length} Módulos</span>
        <span className="text-neutral-300">•</span>
        <span>8 Aulas</span>
        <span className="text-neutral-300">•</span>
        <span>11h 45m de conteúdo</span>
      </div>

      {/* 2. Lista de Módulos */}
      <div className="flex flex-col gap-4">
        {modulesMock.map((module) => {
          const isOpen = openModules.includes(module.id);

          return (
            <div key={module.id} className="border border-neutral-200 rounded-lg overflow-hidden bg-white">
              
              {/* Cabeçalho Clicável */}
              <button 
                onClick={() => toggleModule(module.id)}
                className="w-full flex items-center justify-between p-5 bg-neutral-50 hover:bg-neutral-100 transition-colors text-left cursor-pointer"
              >
                <div className="flex flex-col gap-1">
                  <span className="font-bold text-neutral-900 text-lg">
                    {module.title}
                  </span>
                  <span className="text-xs text-neutral-500 font-medium">
                    {module.lessons.length} aulas • {module.duration}
                  </span>
                </div>
                
                {/* Ícone da Seta */}
                <div className="text-neutral-500">
                  {isOpen ? <FaChevronUp /> : <FaChevronDown />}
                </div>
              </button>

              {/* Lista de Aulas (Visível apenas se isOpen = true) */}
              {isOpen && (
                <div className="border-t border-neutral-200 divide-y divide-neutral-100">
                  {module.lessons.map((lesson) => (
                    <Link to={"aulas?"+lesson.id} key={lesson.id} className="p-4 pl-6 flex items-center justify-between hover:bg-neutral-50 transition-colors group cursor-pointer bg-white">
                      
                      <div className="flex items-center gap-4">
                        <FaPlayCircle className="text-neutral-300 group-hover:text-neutral-500 text-xl shrink-0" />
                        <span className="text-sm font-medium text-neutral-700">
                          {lesson.title}
                        </span>
                      </div>

                      <div className="flex items-center gap-4">
                         {lesson.isFree ? (
                           <span className="text-[10px] font-bold text-neutral-800 border border-neutral-400 bg-white px-2 py-0.5 rounded uppercase tracking-wide">
                             {isProtectedRoute ? "Disponível" : "Grátis"}
                           </span>
                         ) : (
                           <FaLock className="text-neutral-300 text-xs" />
                         )}
                         <span className="text-xs text-neutral-400 w-10 text-right">
                            {lesson.duration}
                         </span>
                      </div>

                    </Link>
                  ))}
                </div>
              )}

            </div>
          );
        })}
      </div>

    </div>
  );
}