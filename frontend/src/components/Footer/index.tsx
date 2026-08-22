import { brandIdentity, BrandLogo } from "@/brand";
import { Link } from "react-router-dom";
import { tv } from "tailwind-variants";

const footer = tv({
    slots: {
        root: "w-full border-t border-border bg-surface-subtle px-4 py-8 xs:px-5",
        container: "mx-auto flex w-full max-w-[1200px] flex-col gap-10 md:gap-12",
        content: "grid min-w-0 grid-cols-1 gap-8 xs:grid-cols-2 md:grid-cols-[minmax(0,2fr)_repeat(3,minmax(0,1fr))] md:gap-10",
        brand: "flex min-w-0 flex-col gap-4 xs:col-span-2 md:col-span-1",
        logo: "h-8 max-w-full w-auto self-start",
        description: "max-w-[300px] text-sm leading-5 text-text-muted",
        column: "flex min-w-0 flex-col gap-4",
        heading: "text-base leading-6 text-text",
        linkList: "flex min-w-0 flex-col gap-2",
        link: "link-black break-words text-sm transition-colors",
        bottom: "flex items-center justify-center border-t border-border pt-8",
        copyright: "max-w-full text-center text-sm text-text-muted",
    },
});

const { root, container, content, brand, logo, description, column, heading, linkList, link, bottom, copyright } = footer();

export default function Footer(): React.ReactElement {
    return (
        <footer className={root()}>
            <div className={container()}>
                <div className={content()}>
                    <div className={brand()}>
                        <BrandLogo className={logo()} />
                        <p className={description()}>{brandIdentity.description}</p>
                    </div>

                    <div className={column()}>
                        <h3 className={heading()}>Plataforma</h3>
                        <ul className={linkList()}>
                            <li><Link to="/explorar" className={link()}>Explorar Cursos</Link></li>
                            <li><Link to="/register" className={link()}>Seja um Professor</Link></li>
                        </ul>
                    </div>

                    <div className={column()}>
                        <h3 className={heading()}>{brandIdentity.shortName}</h3>
                        <ul className={linkList()}>
                            <li><Link to="/sobre" className={link()}>Sobre Nós</Link></li>
                            <li><Link to="/contato" className={link()}>Contato</Link></li>
                        </ul>
                    </div>

                    <div className={column()}>
                        <h3 className={heading()}>Legal</h3>
                        <ul className={linkList()}>
                            <li><Link to="/privacidade" className={link()}>Política de Privacidade</Link></li>
                            <li><Link to="/termos" className={link()}>Termos de Serviço</Link></li>
                        </ul>
                    </div>
                </div>

                <div className={bottom()}>
                    <p className={copyright()}>{brandIdentity.copyright}</p>
                </div>
            </div>
        </footer>
    );
}
