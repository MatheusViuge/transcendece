import { Button } from "@/components/Button";
import { EmptyState, Icon } from "@/design-system";
import { Link } from "react-router-dom";

export default function NotFound() {
    return (
        <div className="grid min-h-[60vh] place-items-center p-4">
            <EmptyState
                icon="search"
                title="Página não encontrada"
                description="O endereço acessado não existe ou foi movido."
                action={
                    <Link to="/" className="block w-full">
                        <Button fullWidth variant="secondary">
                            <Icon name="back" />
                            Voltar para Home
                        </Button>
                    </Link>
                }
            />
        </div>
    );
}
