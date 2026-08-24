import { Navigate, Route, Routes } from "react-router-dom";

import AdminUsers from "@/pages/Admin/Users";
import DashboardAluno from "@/pages/Aluno/Dashboard";
import Files from "@/pages/Files";
import NotFound from "@/pages/NotFound";
import PaginaEmConstrucao from "@/pages/PaginaEmConstrucao";
import Profile from "@/pages/Profile";
import CourseDetails from "@/pages/Publico/CourseDetails";
import DesignSystem from "@/pages/Publico/DesignSystem";
import Explore from "@/pages/Publico/Explore";
import Home from "@/pages/Publico/Home";
import Login from "@/pages/Publico/Login";
import PrivacyPolicy from "@/pages/Publico/PrivacyPolicy";
import Register from "@/pages/Publico/Register";
import TermsOfService from "@/pages/Publico/TermsOfService";
import { PrivateRoute } from "@/pages/Layout/PrivateRoute";

export function AppRoutes() {
    return (
        <Routes>
            <Route element={<PrivateRoute />}>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/recuperar-senha" element={<PaginaEmConstrucao />} />

                <Route path="/explorar" element={<Explore />} />
                <Route path="/cursos/:id" element={<CourseDetails />} />

                <Route path="/sobre" element={<PaginaEmConstrucao />} />
                <Route path="/contato" element={<PaginaEmConstrucao />} />
                <Route path="/privacidade" element={<PrivacyPolicy />} />
                <Route path="/termos" element={<TermsOfService />} />
                <Route path="/design-system" element={<DesignSystem />} />

                <Route path="/perfil" element={<Profile />} />
                <Route path="/usuarios/:userId" element={<Profile />} />

                <Route path="/instrutor">
                    <Route index element={<Navigate to="/instrutor/dashboard" replace />} />
                    <Route path="dashboard" element={<PaginaEmConstrucao />} />
                    <Route path="cursos" element={<PaginaEmConstrucao />} />
                    <Route path="cursos/:id/editar" element={<PaginaEmConstrucao />} />
                    <Route path="correcoes" element={<PaginaEmConstrucao />} />
                    <Route path="arquivos" element={<Files />} />
                </Route>

                <Route path="/aluno">
                    <Route index element={<Navigate to="/aluno/cursos" replace />} />
                    <Route path="explorar" element={<Explore />} />
                    <Route path="cursos" element={<DashboardAluno />} />
                    <Route path="cursos/:id" element={<CourseDetails />} />
                    <Route path="cursos/:id/aulas" element={<PaginaEmConstrucao />} />
                    <Route path="certificados" element={<PaginaEmConstrucao />} />
                    <Route path="arquivos" element={<Files />} />
                </Route>

                <Route path="/admin">
                    <Route index element={<Navigate to="/admin/usuarios" replace />} />
                    <Route path="dashboard" element={<PaginaEmConstrucao />} />
                    <Route path="usuarios" element={<AdminUsers />} />
                    <Route path="cursos" element={<PaginaEmConstrucao />} />
                    <Route path="cursos/:id/editar" element={<PaginaEmConstrucao />} />
                    <Route path="solicitacoes" element={<PaginaEmConstrucao />} />
                    <Route path="arquivos" element={<Files />} />
                </Route>

                <Route path="*" element={<NotFound />} />
            </Route>
        </Routes>
    );
}
