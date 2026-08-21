import { createContext } from "react";

export interface IUserStorage {
    nome: string;
    tipo_usuario: "aluno" | "instrutor" | "admin";
}

export interface IUserContext {
    user: IUserStorage | null;
    login: (body: { email: string; senha: string }) => Promise<void>;
    logout: () => void;
    loading: boolean;
    isAuthenticated: boolean;
}

export const UserContext = createContext<IUserContext | null>(null);
