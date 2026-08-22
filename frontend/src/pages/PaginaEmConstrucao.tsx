import { Button } from "@/components/Button";
import { EmptyState, Icon } from "@/design-system";
import { Link } from "react-router-dom";

export default function PaginaEmConstrucao() {
    return (
        <div className="grid h-full place-items-center p-4">
            <EmptyState
                icon="hammer"
                title="Funcionalidade a caminho!"
                description="Esta página ainda não foi implementada. Estamos polindo os últimos detalhes."
                action={
                    <Link to="/" className="block w-full">
                        <Button fullWidth>
                            <Icon name="back" />
                            Voltar para Home
                        </Button>
                    </Link>
                }
            />
        </div>
    );
}
