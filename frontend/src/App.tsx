import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Home from "@/pages/Publico/Home";
import Login from "@/pages/Publico/Login";
import NotFound from "@/pages/NotFound";
import Register from "@/pages/Publico/Register";
import { Loader } from "@/pages/Layout/Loader";
import { PrivateRoute } from "@/pages/Layout/PrivateRoute";
import PaginaEmConstrucao from "@/pages/PaginaEmConstrucao";
import CourseDetails from "@/pages/Publico/CourseDetails";
import Explore from "@/pages/Publico/Explore";
import DashboardAluno from "@/pages/Aluno/Dashboard";

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route element={<PrivateRoute />} loader={() => <Loader />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/recuperar-senha" element={<PaginaEmConstrucao />} />

                    <Route path="/explorar" element={<Explore />} />
                    <Route path="/cursos/:id" element={<CourseDetails />} />

                    <Route path="/sobre" element={<PaginaEmConstrucao />} />
                    <Route path="/contato" element={<PaginaEmConstrucao />} />
                    <Route path="/privacidade" element={<PaginaEmConstrucao />} />
                    <Route path="/termos" element={<PaginaEmConstrucao />} />

                    <Route path="/instrutor">
                        <Route index element={<Navigate to={"/instrutor/dashboard"} />} />

                        <Route path="/instrutor/dashboard" element={<PaginaEmConstrucao />} />
                        <Route path="/instrutor/cursos" element={<PaginaEmConstrucao />} />
                        <Route path="/instrutor/cursos/:id/editar" element={<PaginaEmConstrucao />} />
                        <Route path="/instrutor/correcoes" element={<PaginaEmConstrucao />} />
                    </Route>

                    <Route path="/aluno">
                        <Route index element={<Navigate to={"/aluno/cursos"} />} />

                        <Route path="/aluno/explorar" element={<Explore />} />
                        <Route path="/aluno/cursos" element={<DashboardAluno />} />
                        <Route path="/aluno/cursos/:id" element={<CourseDetails />} />
                        <Route path="/aluno/cursos/:id/aulas" element={<PaginaEmConstrucao />} />
                        <Route path="/aluno/certificados" element={<PaginaEmConstrucao />} />
                    </Route>

                    <Route path="/admin">
                        <Route index element={<Navigate to={"/admin/dashboard"} />} />

                        <Route path="/admin/dashboard" element={<PaginaEmConstrucao />} />
                        <Route path="/admin/usuarios" element={<PaginaEmConstrucao />} />
                        <Route path="/admin/cursos" element={<PaginaEmConstrucao />} />
                        <Route path="/admin/cursos/:id/editar" element={<PaginaEmConstrucao />} />
                        <Route path="/admin/solicitacoes" element={<PaginaEmConstrucao />} />
                    </Route>

                    <Route path="*" element={<NotFound />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

