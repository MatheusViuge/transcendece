import { createContext } from "react";

export interface IUserStorage {
    id: number;
    nome: string;
    email: string;
    tipo_usuario: "aluno" | "instrutor" | "admin";
}

export interface IUserContext {
    user: IUserStorage | null;
    login: (body: { email: string; senha: string }) => Promise<void>;
    logout: () => void;
    refreshUser: () => Promise<void>;
    loading: boolean;
    isAuthenticated: boolean;
}

export const UserContext = createContext<IUserContext | null>(null);
