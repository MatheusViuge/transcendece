import { api, catchCustom } from "@/services/api";
import { useEffect, useState } from "react";
import { UserContext, type IUserStorage } from "./userContextDefinition";

export function UserProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<IUserStorage | null>(null);
    const [loading, setLoading] = useState(true);

    const authMe = async (token: string) => {
        setLoading(true);

        try {
            const responseAuth = await api.get({ url: "/auth/me", hiddenToast: true });
            const authenticatedUser = responseAuth?.data as IUserStorage;
            setUser(authenticatedUser);
        } catch (error) {
            setUser(null);
            localStorage.removeItem("token");
            throw error;
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const token = localStorage.getItem("token");

        if (!token) {
            setLoading(false);
            return;
        }

        void authMe(token).catch((error) => {
            catchCustom(error);
        });
    }, []);

    const login = async (body: { email: string; senha: string }) => {
        setLoading(true);

        try {
            const responseLogin = await api.post<typeof body>({ url: "/auth/login", body });
            const token = responseLogin?.data?.access_token;

            if (!token) {
                throw new Error("Token de autenticação não retornado pela API.");
            }

            localStorage.setItem("token", token);
            await authMe(token);
        } catch (error) {
            localStorage.removeItem("token");
            setUser(null);
            catchCustom(error);
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
        setLoading(false);
    };

    return (
        <UserContext.Provider value={{ user, login, logout, loading, isAuthenticated: Boolean(user) }}>
            {children}
        </UserContext.Provider>
    );
}
