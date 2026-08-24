import { Link, useNavigate } from "react-router-dom";
import { tv } from "tailwind-variants";
import { BrandLogo } from "@/brand";
import { Button } from "./Button";
import { useUser } from "@/hooks/useUser";
import { ROLE_NAV_LINKS } from "@/routes/access";

const styles = tv({
    slots: {
        navbar: "fixed z-50 flex h-navbar w-full items-center justify-between gap-2 border-b border-border bg-surface px-2 xs:px-4 md:px-[7.3vw]",
    }
});

const { navbar } = styles();

export default function Navbar() {
    const navigate = useNavigate();
    const { user, isAuthenticated, logout } = useUser();
    const roleLinks = user ? ROLE_NAV_LINKS[user.tipo_usuario] : [];

    const handleLogout = () => {
        logout();
        navigate("/login", { replace: true });
    };

    return (
        <nav className={navbar()} aria-label="Navegação principal">
            <Link to="/" className="shrink-0" aria-label="Ir para a página inicial">
                <BrandLogo compact className="h-8 w-auto xs:hidden" />
                <BrandLogo className="hidden h-8 w-auto xs:inline" />
            </Link>

            {isAuthenticated ? (
                <div className="flex min-w-0 flex-1 items-center justify-end gap-1 xs:gap-2 md:gap-3">
                    <div className="flex min-w-0 items-center gap-3 overflow-x-auto whitespace-nowrap py-2 text-sm xs:gap-4">
                        {roleLinks.map((link) => (
                            <Link key={link.to} to={link.to} className="link-black shrink-0 text-sm xs:text-base">
                                {link.label}
                            </Link>
                        ))}
                    </div>
                    <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={handleLogout}
                        className="shrink-0 px-2 text-text-muted opacity-60 hover:border-danger hover:bg-surface-muted hover:text-danger hover:opacity-100 focus-visible:border-danger focus-visible:text-danger focus-visible:opacity-100 xs:px-3"
                        aria-label="Sair da conta"
                        title="Sair da conta"
                    >
                        Sair
                    </Button>
                </div>
            ) : (
                <div className="flex min-w-0 items-center justify-end gap-1 xs:gap-2 md:gap-4">
                    <Link to="/explorar" className="hidden md:inline link-black">Explorar Cursos</Link>
                    <Link to="/login" className="shrink-0">
                        <Button variant="secondary" className="px-2 text-sm xs:px-4">Entrar</Button>
                    </Link>
                    <Link to="/register" className="shrink-0">
                        <Button className="px-2 text-sm xs:px-4">Cadastre-se</Button>
                    </Link>
                </div>
            )}
        </nav>
    );
}
