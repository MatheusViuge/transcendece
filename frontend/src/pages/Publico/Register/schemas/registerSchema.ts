import { z } from "zod";

export const registerSchema = z.object({
  nome: z.string().min(1, "Campo obrigatório"),
  sobrenome: z.string().min(1, "Campo obrigatório"),
  data_nascimento: z.string().min(1, "Campo obrigatório"),
  email: z.string().min(1, "Campo obrigatório").email("Formato de email inválido"),
  senha_hash: z.string()
    .min(6, "Mínimo 6 caracteres")
    .regex(/[a-zA-Z]/, "Pelo menos uma letra")
    .regex(/\d/, "Pelo menos um número")
    .regex(/[!@#$%^&*(),.?":{}|<>]/, "Pelo menos um caractere especial"),
  confirmPassword: z.string().min(1, "Confirmação obrigatória"),
  acceptedTerms: z.boolean().refine((val) => val === true, {
    message: "Você precisa aceitar os termos de uso",
  }),
}).refine((data) => data.senha_hash === data.confirmPassword, {
  path: ["confirmPassword"],
  message: "As senhas não coincidem",
});

export type RegisterFormData = z.infer<typeof registerSchema>;