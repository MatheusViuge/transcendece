import { Link } from "react-router-dom";

import { Button } from "@/components/Button";
import { useUser } from "@/hooks/useUser";
import { getRoleLandingPath } from "@/routes/access";

export default function Forbidden() {
    const { user } = useUser();
    const destination = user ? getRoleLandingPath(user.tipo_usuario) : "/";

    return (
        <main className="mx-auto flex min-h-[60vh] max-w-2xl flex-col items-center justify-center gap-4 px-6 text-center">
            <p className="text-sm font-semibold uppercase tracking-wide text-text-muted">403</p>
            <h1 className="text-3xl font-semibold text-text-primary">Você não tem permissão para acessar esta área.</h1>
            <p className="max-w-xl text-text-muted">
                A interface respeita sua role atual, mas a autorização definitiva continua sendo validada pelo backend.
            </p>
            <Link to={destination}>
                <Button>Voltar para minha área</Button>
            </Link>
        </main>
    );
}
