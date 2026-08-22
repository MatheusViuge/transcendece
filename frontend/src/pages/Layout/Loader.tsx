import { BrandLogo } from "@/brand";

export function Loader() {
    return (
        <div className="z-50 grid h-screen w-screen place-items-center" role="status" aria-label="Carregando aplicação">
            <BrandLogo compact alt="" aria-hidden="true" className="h-30 animate-pulse duration-2000" />
        </div>
    );
}
