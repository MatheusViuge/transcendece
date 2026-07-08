import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

// Importando o schema e o tipo que define a estrutura do formulário
import { registerSchema, type RegisterFormData } from "../schemas/registerSchema";
import { api, catchCustom } from "@/services/api";

// Re-exportando o tipo para que o componente visual (index.tsx) possa usar se precisar
export type { RegisterFormData };

export function useRegisterForm() {
  const [isSuccess, setIsSuccess] = useState(false);

  // Configuração do React Hook Form usando o schema importado
  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      acceptedTerms: false,
    },
  });

  // Função de envio do formulário
  const onSubmit = async (data: RegisterFormData) => {
    try {
      await api.post({ url: "/auth/register", body: data });
      setIsSuccess(true);
    } catch (error) {
      catchCustom(error);
    }
  };

  // Retorna tudo que a tela precisa para funcionar
  return {
    form,
    isSuccess,
    onSubmit: form.handleSubmit(onSubmit), 
  };
}