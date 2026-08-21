import { z } from "zod";

export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, "O email é obrigatório")
    .max(254, "O email é muito longo")
    .email("Formato de email inválido")
    .transform((value) => value.toLowerCase()),
  senha: z
    .string()
    .min(1, "A senha é obrigatória")
    .max(128, "A senha é muito longa"),
});

export type LoginFormData = z.infer<typeof loginSchema>;
