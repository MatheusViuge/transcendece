import type { UseFormReturn } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/Button";
import { Input } from "@/components/Form/Input";
import { PasswordStrength } from "./PasswordStrength";
import type { RegisterFormData } from "../hooks/useRegisterForm";
import { ContainerInputs } from "@/components/Form";

interface RegisterFormProps {
  form: UseFormReturn<RegisterFormData>;
  onSubmit: () => void;
  onOpenTerms: () => void;
}

export function RegisterForm({ form, onSubmit, onOpenTerms }: RegisterFormProps) {
  const navigate = useNavigate();
  const { register, watch, formState: { errors } } = form;
  
  const passwordValue = watch("senha_hash") || "";
  
  // Cast seguro para erros
  const formErrors = errors as unknown as Record<string, Record<string, string>>;

  return (
    <form onSubmit={onSubmit}>
      <ContainerInputs>
        <Input
          id="nome"
          label="Nome"
          placeholder="Digite seu nome"
          {...register("nome")}
          errors={formErrors}
        />

        <Input
          id="sobrenome"
          label="Sobrenome"
          placeholder="Digite seu sobrenome"
          {...register("sobrenome")}
          errors={formErrors}
        />

        <Input
          id="data_nascimento"
          label="Data de Nascimento"
          type="date"
          placeholder="Digite sua data de nascimento"
          {...register("data_nascimento")}
          errors={formErrors}
        />

        <Input
          id="email"
          type="email"
          label="Email"
          placeholder="seu@email.com"
          {...register("email")}
          errors={formErrors}
        />

        <div>
          <Input
            id="senha_hash"
            type="password"
            label="Senha"
            placeholder="••••••••"
            {...register("senha_hash")}
            errors={formErrors}
          />
          <PasswordStrength password={passwordValue} />
        </div>

        <Input
          id="confirmPassword"
          type="password"
          label="Confirmar Senha"
          placeholder="••••••••"
          {...register("confirmPassword")}
          errors={formErrors}
        />

        <Input
          type="checkbox"
          id="acceptedTerms"
          label={
            <>
                Li e concordo com os{" "}
                <button
                  type="button"
                  onClick={onOpenTerms}
                  className="text-blue hover:underline cursor-pointer"
                >Termos de Uso</button>{" "}
                e Política de Privacidade.
            </>
          }
          {...register("acceptedTerms")}
        />

        {errors.acceptedTerms && (
          <p className="text-xs text-red mt-1">{errors.acceptedTerms.message}</p>
        )}

        <Button fullWidth type="submit">Criar Conta</Button>

        <Button fullWidth variant="secondary" type="button" onClick={() => navigate("/")}>
          Voltar
        </Button>
      </ContainerInputs>
    </form>
  );
}