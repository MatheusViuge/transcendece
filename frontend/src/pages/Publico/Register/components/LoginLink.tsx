import { Link } from "react-router-dom";

export function LoginLink() {
  return (
    <p className="text-center text-sm black-text pt-2">
      Já possui conta?{" "}
      <Link 
        to="/login" 
        className="link"
      >
        Entrar
      </Link>
    </p>
  );
}