import { useUser } from "@/hooks/useUser";
import { Navigate, useLocation } from "react-router-dom";
import { Layout } from "./Layout";
import { Loader } from "./Loader";

const protectedBasePaths = ["/instrutor", "/aluno", "/admin"] as const;

export function PrivateRoute() {
    const { user, loading, isAuthenticated } = useUser();
    const role = user?.tipo_usuario;
    const pathname = useLocation().pathname;
    const protectedBasePath = protectedBasePaths.find(
        (path) => pathname === path || pathname.startsWith(`${path}/`),
    );

    if (loading) return <Loader />;

    if (!protectedBasePath) return <Layout />;

    if (!isAuthenticated) return <Navigate to="/login" replace />;

    const expectedRole = protectedBasePath.slice(1);

    if (role !== expectedRole) {
        return <Navigate to={role ? `/${role}` : "/"} replace />;
    }

    return <Layout />;
}
