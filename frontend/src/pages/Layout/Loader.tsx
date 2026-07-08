import logoBlack from "@/assets/simbolo_black.svg";

export function Loader() {
    return (
        <div className="grid h-screen w-screen z-50 place-items-center">
            <img src={logoBlack} alt="Carregando..." className="h-30 animate-pulse duration-2000" />
        </div>
    );
}