import { api, catchCustom } from "@/services/api";
import { createContext, useEffect, useState } from "react";

interface IUserStorage {
    nome: string;
    tipo_usuario: "aluno" | "instrutor" | "admin";
}

interface IUserContext {
    user: IUserStorage|null;
    login: (body: { email: string; senha: string }) => Promise<void>;
    logout: () => void;
    loading: boolean;
    isAuthenticated: boolean;
}

export const UserContext = createContext<IUserContext|null>(null);

export function UserProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<IUserStorage|null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');

        if (!token) {
            setLoading(false);
            return;
        }

        (async () => {
            try {
                await authMe(token);
            } catch (err) {
                catchCustom(err);
            }
        })()
    }, []);

    const authMe = async (token: string) => {
        setLoading(true);

        try {
            const responseAuth = await api.get({ url: '/auth/me' });
            const user = responseAuth?.data;

            setUser({ ...user, token });
        } catch (err) {
            setUser(null);
            localStorage.removeItem('token');
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const login = async (body: { email: string; senha: string }) => {
        setLoading(true);

        try {
            const responseLogin = await api.post<typeof body>({ url: '/auth/login', body });
            const token = responseLogin?.data?.access_token;

            localStorage.setItem('token', token);

            await authMe(token);
        } catch (err) {
            localStorage.removeItem('token');
            catchCustom(err);
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
        setLoading(false);
    };

    return (
        <UserContext.Provider value={{ user, login, logout, loading, isAuthenticated: !!user }}>
            { children }
        </UserContext.Provider>
    );
}
