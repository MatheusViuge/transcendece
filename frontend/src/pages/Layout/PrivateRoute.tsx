import { useUser } from "@/hooks/useUser";
import { getRequiredRole, getRoleLandingPath } from "@/routes/access";
import { Navigate, useLocation } from "react-router-dom";
import { Layout } from "./Layout";
import { Loader } from "./Loader";

export function PrivateRoute() {
    const { user, loading, isAuthenticated } = useUser();
    const pathname = useLocation().pathname;
    const requiredRole = getRequiredRole(pathname);

    if (loading) return <Loader />;
    if (!requiredRole) return <Layout />;
    if (!isAuthenticated) return <Navigate to="/login" replace />;

    if (user?.tipo_usuario !== requiredRole) {
        return (
            <Navigate
                to={user ? getRoleLandingPath(user.tipo_usuario) : "/"}
                replace
            />
        );
    }

    return <Layout />;
}
