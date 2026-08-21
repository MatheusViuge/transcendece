import { Link } from "react-router-dom";
import { tv } from "tailwind-variants";
import simbolo from "@/assets/simbolo_black.svg";
import logo from "@/assets/logo_black.svg";
import { Button } from "./Button";
import { useUser } from "@/hooks/useUser";

const styles = tv({
    slots: {
        navbar: "fixed z-50 flex h-navbar w-full items-center justify-between gap-2 border-b border-overlay bg-white px-2 xs:px-4 md:px-[7.3vw]",
    }
});

const { navbar } = styles();

type Role = "aluno" | "instrutor" | "admin";

const links: Record<Role, Array<{ label: string; to: string }>> = {
    aluno: [
        { label: "Explorar", to: "/aluno/explorar" },
        { label: "Atividades", to: "/aluno/atividades" },
    ],
    instrutor: [
        { label: "Meus Cursos", to: "/instrutor/meus-cursos" },
        { label: "Correções", to: "/instrutor/correcoes" },
    ],
    admin: [
        { label: "Usuários", to: "/admin/usuarios" },
        { label: "Cursos", to: "/admin/cursos" },
    ],
};

export default function Navbar() {
    const { user, isAuthenticated } = useUser();
    const roleLinks = user?.tipo_usuario && user.tipo_usuario in links
        ? links[user.tipo_usuario as Role]
        : [];

    return (
        <nav className={navbar()} aria-label="Navegação principal">
            <Link to="/" className="shrink-0" aria-label="Ir para a página inicial">
                <img className="h-8 w-auto xs:hidden" src={simbolo} alt="Instituto Consuelo" />
                <img className="hidden h-8 w-auto xs:inline" src={logo} alt="Instituto Consuelo" />
            </Link>

            {isAuthenticated ? (
                <div className="flex max-w-[72vw] items-center gap-3 overflow-x-auto whitespace-nowrap py-2 text-sm xs:gap-4">
                    {roleLinks.map((link) => (
                        <Link key={link.to} to={link.to} className="link-black shrink-0 text-sm xs:text-base">
                            {link.label}
                        </Link>
                    ))}
                </div>
            ) : (
                <div className="flex min-w-0 items-center justify-end gap-1 xs:gap-2 md:gap-4">
                    <Link to="/explorar" className="hidden md:inline link-black">Explorar Cursos</Link>
                    <Link to="/login" className="shrink-0">
                        <Button variant="secondary" className="border-overlay px-2 text-sm xs:px-4">Entrar</Button>
                    </Link>
                    <Link to="/register" className="shrink-0">
                        <Button className="px-2 text-sm xs:px-4">Cadastre-se</Button>
                    </Link>
                </div>
            )}
        </nav>
    );
}
