import { BrandLogo } from "@/brand";
import { Button } from "@/components/Button";
import { Alert } from "@/design-system";
import { Link } from "react-router-dom";

export function SuccessMessage() {
  return (
    <div className="space-y-6 text-center animate-fade-in">
      <div className="mb-4 flex justify-center">
        <BrandLogo compact className="h-16 w-auto opacity-50" />
      </div>
      <Alert tone="success" title="Conta criada com sucesso!">
        Seja bem-vindo(a)! Sua conta de estudante foi registrada.
      </Alert>
      <div className="pt-4">
        <Link to="/login">
          <Button fullWidth type="button">Ir para o Login</Button>
        </Link>
      </div>
    </div>
  );
}
