import { Link } from "react-router-dom";
import { Button } from "@/components/Button";
import simbolo from "@/assets/simbolo_black.svg";

export function SuccessMessage() {
  return (
    <div className="text-center space-y-6 animate-fade-in">
      <div className="flex justify-center mb-4">
        <img src={simbolo} alt="Logo" className="h-16 w-auto opacity-50" />
      </div>
      <h2 className="text-2xl font-bold text-green-600">Conta criada com sucesso!</h2>
      <p className="text-gray-600">Seja bem-vindo(a)! Sua conta de estudante foi registrada.</p>
      <div className="pt-4">
        <Link to="/login">
          <Button fullWidth type="button">Ir para o Login</Button>
        </Link>
      </div>
    </div>
  );
}