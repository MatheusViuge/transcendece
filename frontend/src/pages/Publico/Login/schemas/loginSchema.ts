import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().trim().min(1, "O email é obrigatório").email("Formato de email inválido"),
  senha: z.string().min(1, "A senha é obrigatória"),
});

export type LoginFormData = z.infer<typeof loginSchema>;