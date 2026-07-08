import { Link } from "react-router-dom";
import { tv } from "tailwind-variants";
import simbolo from "@/assets/simbolo_black.svg";
import logo from "@/assets/logo_black.svg";
import { Button } from "./Button";
import { useUser } from "@/hooks/useUser";

const styles = tv({
    slots: {
        navbar: "fixed flex justify-between items-center bg-white px-4 xs:px-[7.3vw] h-navbar w-full border-b border-overlay z-50",
    }
});

const { navbar } = styles();

export default function Navbar() {
    const { user, isAuthenticated } = useUser();

    const links = {
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
        "": []
    };

    return (
        <nav className={navbar()}>
            <Link to="/">
                <img className="xs:hidden" src={simbolo} alt="Logo Instituto Consuelo" />
                <img className="hidden xs:inline" src={logo} alt="Logo Instituto Consuelo" />
            </Link>

            <div className="flex justify-end items-center gap-4">
                { isAuthenticated
                ?
                    links[user?.tipo_usuario||""].map((link:any) => (
                        <Link key={link.to} to={link.to} className="link-black">{link.label}</Link>
                    ))
                :
                    <>
                        <Link to="/explorar" className="hidden md:inline link-black">Explorar Cursos</Link>
                        <Link to="/login"><Button variant="secondary" className="border-overlay">Entrar</Button></Link>
                        <Link to="/register"><Button>Cadastre-se</Button></Link>
                    </>
                }
            </div>
        </nav>
    );
}