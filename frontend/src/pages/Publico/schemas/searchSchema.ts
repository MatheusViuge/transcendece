import { z } from "zod";

export const searchSchema = z.object({
  busca: z
    .string()
    .trim()
    .max(120, "A busca deve possuir no máximo 120 caracteres"),
});

export type SearchFormData = z.infer<typeof searchSchema>;
