import { useUser } from "@/hooks/useUser";
import Forbidden from "@/pages/Forbidden";
import { getRequiredRole, isAuthenticatedOnlyPath } from "@/routes/access";
import { Navigate, useLocation } from "react-router-dom";
import { Layout } from "./Layout";
import { Loader } from "./Loader";

export function PrivateRoute() {
    const { user, loading, isAuthenticated } = useUser();
    const pathname = useLocation().pathname;
    const requiredRole = getRequiredRole(pathname);
    const authOnly = isAuthenticatedOnlyPath(pathname);

    if (loading && !user) return <Loader />;
    if (authOnly && !isAuthenticated) return <Navigate to="/login" replace />;
    if (!requiredRole) return <Layout />;
    if (!isAuthenticated) return <Navigate to="/login" replace />;

    if (user?.tipo_usuario !== requiredRole) {
        return (
            <Layout>
                <Forbidden />
            </Layout>
        );
    }

    return <Layout />;
}
