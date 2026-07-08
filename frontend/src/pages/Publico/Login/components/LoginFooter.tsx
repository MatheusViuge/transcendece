import { Link } from "react-router-dom";

export function LoginFooter() {
  return (
    <div>
      <p className="text-center black-text text-sm">
        Não possui conta?{" "}
        <Link to="/register" className="link font-medium">
          Criar conta
        </Link>
      </p>
    </div>
  );
}