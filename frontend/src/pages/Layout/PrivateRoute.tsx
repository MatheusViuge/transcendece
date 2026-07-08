import { useUser } from "@/hooks/useUser";
import { useLocation, Navigate } from "react-router-dom";
import { Layout } from "./Layout";
import { Loader } from "./Loader";

export const basedPathProtected = ["/instrutor", "/aluno", "/admin"];

export function PrivateRoute() {
    const { user, loading, isAuthenticated } = useUser();
    const role = user?.tipo_usuario;

    const from = useLocation().pathname;
    const roleBasedPath = from.split("/")[1] || "/";

    if (loading)
        return <Loader />;

    if (!isAuthenticated && basedPathProtected.some((path) => from.startsWith(path)))
        return <Navigate to={"/login"} />;

    if (isAuthenticated && role !== roleBasedPath)
        return <Navigate to={"/"+role} />;

    return <Layout />;
}
