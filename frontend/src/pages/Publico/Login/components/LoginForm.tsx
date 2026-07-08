import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/Button";
import { Input } from "@/components/Form/Input";
import { loginSchema, type LoginFormData } from "../schemas/loginSchema";
import { ContainerInputs } from "@/components/Form/ContainerInputs";
import { catchCustom } from "@/services/api";
import { useUser } from "@/hooks/useUser";

export function LoginForm() {
  const { login } = useUser();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data);
      navigate("/");
    } catch (error) {
      catchCustom(error);
    }
  };

  const formErrors = errors as unknown as Record<string, Record<string, string>>;

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <ContainerInputs>
        <Input
          id="email"
          type="email"
          label="Email"
          placeholder="seu@email.com"
          autoFocus
          autoComplete="email"
          {...register("email")}
          errors={formErrors}
        />

        <div className="relative">
          <Input
            id="senha"
            type="password"
            label="Senha"
            placeholder="••••••••"
            autoComplete="current-password"
            {...register("senha")}
            errors={formErrors}
          />

          <Link to="/recuperar-senha" className="link text-sm absolute right-0 top-0">
            Esqueceu sua senha?
          </Link>
        </div>

        <Button fullWidth type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Entrando..." : "Entrar"}
        </Button>

        <Link to="/" className="block">
          <Button fullWidth variant="secondary" type="button">
            Voltar
          </Button>
        </Link>
      </ContainerInputs>
    </form>
  );
}