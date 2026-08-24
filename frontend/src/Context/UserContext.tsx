import { api, catchCustom } from "@/services/api";
import { useCallback, useEffect, useState } from "react";
import { UserContext, type IUserStorage } from "./userContextDefinition";

type LoginResponse = {
    access_token: string;
    token_type: string;
};

const AUTH_STORAGE_KEY = "token";

function clearAuthStorage() {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
}

export function UserProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<IUserStorage | null>(null);
    const [loading, setLoading] = useState(true);

    const authMe = useCallback(async () => {
        setLoading(true);

        try {
            const responseAuth = await api.get<IUserStorage>({ url: "/auth/me", hiddenToast: true });
            setUser(responseAuth.data);
        } catch (error) {
            setUser(null);
            clearAuthStorage();
            throw error;
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const token = localStorage.getItem(AUTH_STORAGE_KEY);

        if (!token) {
            setLoading(false);
            return;
        }

        void authMe().catch((error) => {
            catchCustom(error);
        });
    }, [authMe]);

    useEffect(() => {
        const refreshOnFocus = () => {
            if (!localStorage.getItem(AUTH_STORAGE_KEY)) return;
            void authMe().catch(() => undefined);
        };

        window.addEventListener("focus", refreshOnFocus);
        return () => window.removeEventListener("focus", refreshOnFocus);
    }, [authMe]);

    const login = async (body: { email: string; senha: string }) => {
        setLoading(true);

        try {
            const responseLogin = await api.post<typeof body, LoginResponse>({
                url: "/auth/login",
                body,
            });
            const token = responseLogin.data.access_token;

            if (!token) {
                throw new Error("Token de autenticação não retornado pela API.");
            }

            localStorage.setItem(AUTH_STORAGE_KEY, token);
            await authMe();
        } catch (error) {
            clearAuthStorage();
            setUser(null);
            catchCustom(error);
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        clearAuthStorage();
        setUser(null);
        setLoading(false);
    };

    return (
        <UserContext.Provider
            value={{
                user,
                login,
                logout,
                refreshUser: authMe,
                loading,
                isAuthenticated: Boolean(user),
            }}
        >
            {children}
        </UserContext.Provider>
    );
}
