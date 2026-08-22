import { Alert } from "@/design-system";
import { useOnlineStatus } from "./useOnlineStatus";

export function ConnectivityBanner() {
  const isOnline = useOnlineStatus();

  if (isOnline) return null;

  return (
    <div
      className="fixed inset-x-4 bottom-4 z-100 mx-auto max-w-2xl shadow-dialog"
      aria-live="polite"
    >
      <Alert tone="warning" title="Você está offline">
        Conteúdo já carregado pode continuar disponível. Login, cadastro, uploads e
        outras ações que dependem do servidor precisam de conexão; nenhuma alteração
        será simulada ou enfileirada localmente.
      </Alert>
    </div>
  );
}
