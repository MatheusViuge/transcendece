import { Button } from "@/components/Button";
import { LuClock4 } from "react-icons/lu";

interface TeacherModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function TeacherModal({ isOpen, onClose }: TeacherModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 text-center grid gap-y-4">
        
        {/* Ícone de Relógio/Espera */}
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100 mb-4">
          <LuClock4 className="text-[1.75rem] text-golden" />
        </div>

        <h3 className="text-xl black-text">
          Solicitação Enviada!
        </h3>
        
        <p className="text text-base">
          Como você selecionou o perfil de <strong>Professor</strong>, sua conta precisa passar por uma aprovação da coordenação.
        </p>
        
        <div className="p-4 rounded-lg text text-base text-left">
          <p className="font-bold mb-1">Próximos passos:</p>
          <ul className="list-disc pl-4 grid gap-y-1">
            <li>Aguarde o e-mail de confirmação.</li>
            <li>Nossa equipe validará seus dados em até 24h.</li>
          </ul>
        </div>

        <div className="pt-2">
          <Button fullWidth onClick={onClose}>
            Entendi, vou aguardar
          </Button>
        </div>
      </div>
    </div>
  );
}