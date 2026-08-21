import { z } from "zod";

const requiredName = z
  .string()
  .trim()
  .min(1, "Campo obrigatório")
  .max(80, "Máximo de 80 caracteres");

const birthDateSchema = z
  .string()
  .min(1, "Campo obrigatório")
  .refine((value) => {
    const date = new Date(`${value}T00:00:00`);
    return !Number.isNaN(date.getTime());
  }, "Data de nascimento inválida")
  .refine((value) => {
    const date = new Date(`${value}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  }, "A data de nascimento deve estar no passado");

export const registerSchema = z.object({
  nome: requiredName,
  sobrenome: requiredName,
  data_nascimento: birthDateSchema,
  email: z
    .string()
    .trim()
    .min(1, "Campo obrigatório")
    .max(254, "O email é muito longo")
    .email("Formato de email inválido")
    .transform((value) => value.toLowerCase()),
  senha_hash: z.string()
    .min(6, "Mínimo 6 caracteres")
    .max(128, "Máximo de 128 caracteres")
    .regex(/[a-zA-Z]/, "Pelo menos uma letra")
    .regex(/\d/, "Pelo menos um número")
    .regex(/[!@#$%^&*(),.?":{}|<>]/, "Pelo menos um caractere especial"),
  confirmPassword: z
    .string()
    .min(1, "Confirmação obrigatória")
    .max(128, "Máximo de 128 caracteres"),
  acceptedTerms: z.boolean().refine((val) => val === true, {
    message: "Você precisa aceitar os termos de uso e a política de privacidade",
  }),
}).refine((data) => data.senha_hash === data.confirmPassword, {
  path: ["confirmPassword"],
  message: "As senhas não coincidem",
});

export type RegisterFormData = z.infer<typeof registerSchema>;
