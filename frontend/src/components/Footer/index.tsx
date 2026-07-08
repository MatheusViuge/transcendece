import { Link } from "react-router-dom";
import { tv } from "tailwind-variants";
import logoImg from "@/assets/logo_black.svg";

const footer = tv({
    slots: {
        root: "bg-neutral-25 border-t border-overlay w-full py-8 px-5",
        container: "max-w-[1200px] mx-auto w-full flex flex-col gap-12",
        content: "flex justify-between items-start flex-wrap gap-10",
        brand: "flex flex-col gap-4 max-w-[300px] flex-1 min-w-[250px]",
        logo: "h-8 w-auto self-start",
        description: "text-neutral-600 text-sm leading-5",
        column: "flex flex-col gap-4 min-w-[150px]",
        heading: "text-neutral-900 text-base leading-6",
        linkList: "flex flex-col gap-2",
        link: "link-black text-sm transition-colors",
        bottom: "border-t border-overlay pt-8 flex justify-center items-center",
        copyright: "text-neutral-600 text-sm text-center",
    },
});

const { root, container, content, brand, logo, description, column, heading, linkList, link, bottom, copyright } = footer();

export default function Footer(): React.ReactElement {
    return (
        <footer className={root()}>
            <div className={container()}>

                {/* Seção Superior: Conteúdo Principal */}
                <div className={content()}>
                    {/* Coluna 1: Marca/Logo */}
                    <div className={brand()}>
                        <img className={logo()} alt="Instituto Consuelo Logo" src={logoImg} />
                        <p className={description()}>Capacitando alunos em todo o mundo com educação de qualidade.</p>
                    </div>

                    {/* Coluna 2: Plataforma */}
                    <div className={column()}>
                        <h3 className={heading()}>Plataforma</h3>

                        <ul className={linkList()}>
                            <li>
                                <Link to="/cursos" className={link()}>Explorar Cursos</Link>
                            </li>

                            <li>
                                <Link to="/register" className={link()}>Seja um Professor</Link>
                            </li>
                        </ul>
                    </div>

                    {/* Coluna 3: Consuelo */}
                    <div className={column()}>
                        <h3 className={heading()}>Consuelo</h3>

                        <ul className={linkList()}>
                            <li>
                                <Link to="/sobre" className={link()}>Sobre Nós</Link>
                            </li>

                            <li>
                                <Link to="/contato" className={link()}>Contato</Link>
                            </li>
                        </ul>
                    </div>

                    {/* Coluna 4: Legal */}
                    <div className={column()}>
                        <h3 className={heading()}>Legal</h3>

                        <ul className={linkList()}>
                            <li>
                                <Link to="/privacidade" className={link()}>Política de Privacidade</Link>
                            </li>

                            <li>
                                <Link to="/termos" className={link()}>Termos de Serviço</Link>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Seção Inferior: Copyright */}
                <div className={bottom()}>
                    <p className={copyright()}>© 2025 Instituto Consuelo. Todos os direitos reservados.</p>
                </div>
            </div>
        </footer>
    );
}