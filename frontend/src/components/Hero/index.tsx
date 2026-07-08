import { Button } from '@/components/Button';
import imgHeader from "@/assets/fotoheader.jpg";

export default function Hero() {
  return (
    <header className="grid bg-linear-to-b from-blue-100 to-white relative w-full h-fit min-h-[400px] max-h-[600px] overflow-hidden">

      {/* Imagem de fundo */}
      <img 
        className="hidden sm:block relative inset-0 bg-cover bg-no-repeat bg-[center_20%] sm:bg-[center_40%] md:bg-center"
        src={imgHeader}
        alt="Imagem de fundo do Home"
      />

      {/* Overlay suave para legibilidade */}
      <div className="absolute inset-0 sm:bg-white/70" />

      {/* Conteúdo - Alinhado à esquerda */}
      <div className="grid gap-6 content-center justify-center sm:absolute sm:inset-0 md:justify-start md:content-start p-4 pt-8 md:p-[114.5px] w-full h-full z-20">
        {/* Título com palavra em azul */}
        <h1 className="text-[40px] xs:text-[42px] font-bold text-neutral-900 leading-none">
          Domine as<br />
          Habilidades do<br />
          <span className="text-blue">Futuro</span>
        </h1>

        {/* Subtítulo */}
        <p className="text text-[17.5px] leading-7 max-w-[404px]">
          Impulsione sua carreira e transforme seu potencial em resultados reais. 
          Cursos práticos, instrutores especializados e certificação reconhecida
        </p>

        {/* Botão de Call-to-Action */}
        <Button variant="accent" className='w-fit'>Quero me Inscrever</Button>
      </div>
    </header>
  );
}