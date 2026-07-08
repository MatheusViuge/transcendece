import { Button } from "@/components/Button";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onAccept: () => void;
};

export function TermsModal({ isOpen, onClose, onAccept }: Props) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 space-y-4 relative">
        <h3 className="text-xl font-medium black-text">Termos e Política</h3>

        <div className="h-64 overflow-y-auto text-sm text grid gap-y-4 pr-2 border border-overlay rounded-md p-4 text-justify">
          <div>
            <p className="font-semibold">1. Termos de Uso</p>
            <p>Lorem ipsum dolor sit amet...</p>
          </div>

          <div>
            <p className="font-semibold">2. Política de Privacidade</p>
            <p>Consectetur adipiscing elit...</p>
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