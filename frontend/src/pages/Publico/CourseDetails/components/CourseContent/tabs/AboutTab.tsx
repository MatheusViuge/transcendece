export function AboutTab() {
  return (
    <div className="flex flex-col gap-6 py-6 max-w-4xl">
      
      {/* Seção Sobre */}
      <section className="flex flex-col gap-2"> 
        <h3 className="text-base font-normal leading-6 text-neutral-900">
          Sobre este curso:
        </h3>
        
        <div className="flex flex-col gap-4 text-base font-normal leading-6 text-neutral-900">
            <p>
            Aprenda desenvolvimento web do zero com HTML, CSS, JavaScript, React, Node.js e muito mais.
            </p>
            <p>
            Este curso completo vai te levar do nível iniciante ao avançado. Você vai aprender por meio de projetos práticos e exemplos do mundo real.
            </p>
        </div>
      </section>

      {/* Seção O que você vai aprender */}
      <section className="flex flex-col gap-2">
        <h3 className="text-base font-normal leading-6 text-neutral-900">
          O que você vai aprender:
        </h3>
        
        <ul className="flex flex-col gap-2 text-base font-normal leading-6 text-neutral-900">
          {[
            "Domine os fundamentos e os conceitos avançados",
            "Build real-world projects from scratch",
            "Construa projetos reais do zero",
            "Habilidades de resolução de problemas e pensamento crítico"
          ].map((item, index) => (
            <li key={index} className="flex items-start">
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Seção Professor */}
      <section className="flex flex-col gap-2 pt-2">
        <h3 className="text-base font-normal leading-6 text-neutral-900">
          Professor
        </h3>
        
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-neutral-100 rounded-md flex items-center justify-center text-lg font-medium text-neutral-500 border border-neutral-200">
            G
          </div>
          
          <div className="flex flex-col">
            <h4 className="text-base font-bold text-neutral-900">Guilherme Clemente</h4>
            <p className="text-sm text-neutral-500">Engenheiro de Software</p>
          </div>
        </div>
      </section>

    </div>
  );
}