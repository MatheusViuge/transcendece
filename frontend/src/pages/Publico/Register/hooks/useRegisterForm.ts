import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { registerSchema, type RegisterFormData } from "../schemas/registerSchema";
import { api, catchCustom } from "@/services/api";

export type { RegisterFormData };

type RegisterRequest = Pick<
  RegisterFormData,
  "nome" | "sobrenome" | "data_nascimento" | "email" | "senha_hash"
>;

export function useRegisterForm() {
  const [isSuccess, setIsSuccess] = useState(false);

  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      acceptedTerms: false,
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    const body: RegisterRequest = {
      nome: data.nome,
      sobrenome: data.sobrenome,
      data_nascimento: data.data_nascimento,
      email: data.email,
      senha_hash: data.senha_hash,
    };

    try {
      await api.post<RegisterRequest>({ url: "/auth/register", body });
      setIsSuccess(true);
    } catch (error) {
      catchCustom(error);
    }
  };

  return {
    form,
    isSuccess,
    onSubmit: form.handleSubmit(onSubmit),
  };
}
