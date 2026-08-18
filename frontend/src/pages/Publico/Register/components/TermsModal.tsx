import { Button } from "@/components/Button";
import { Link } from "react-router-dom";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onAccept: () => void;
};

export function TermsModal({ isOpen, onClose, onAccept }: Props) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 animate-fade-in">
      <div
        className="relative w-full max-w-lg space-y-4 rounded-2xl bg-white p-6 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="terms-modal-title"
      >
        <h3 id="terms-modal-title" className="text-xl font-medium black-text">
          Termos e Política
        </h3>

        <div className="grid max-h-64 gap-y-4 overflow-y-auto rounded-md border border-overlay p-4 pr-2 text-sm text text-justify">
          <div className="space-y-2">
            <p className="font-semibold">1. Termos de Uso</p>
            <p>
              Ao criar uma conta, você concorda em utilizar a plataforma de forma compatível com
              sua finalidade educacional, proteger suas credenciais e respeitar as regras de acesso
              e de uso descritas no documento completo.
            </p>
            <Link
              className="inline-block font-medium underline underline-offset-4"
              to="/termos"
              onClick={onClose}
            >
              Ler os Termos de Serviço completos
            </Link>
          </div>

          <div className="space-y-2">
            <p className="font-semibold">2. Política de Privacidade</p>
            <p>
              Tratamos dados de conta e de uso apenas para autenticação, funcionamento da
              plataforma e proteção do serviço. Senhas e segredos de infraestrutura não devem ser
              apresentados em texto simples ao usuário.
            </p>
            <Link
              className="inline-block font-medium underline underline-offset-4"
              to="/privacidade"
              onClick={onClose}
            >
              Ler a Política de Privacidade completa
            </Link>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} type="button">Fechar</Button>
          <Button onClick={onAccept} type="button">Li e Concordo</Button>
        </div>
      </div>
    </div>
  );
}
