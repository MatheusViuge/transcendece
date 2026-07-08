import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import * as Lu from "react-icons/lu"; // Exemplo usando ícones Lucide
import { Link } from "react-router-dom";

export default function PaginaEmConstrucao() {
    return (
        <div className="grid place-items-center p-4 h-full">
            <Card className="grid max-w-md w-full text-center p-8">
                <div className="bg-blue-100 p-4 w-fit h-fit justify-self-center rounded-full">
                    <Lu.LuHammer className="w-12 h-12 text-blue" />
                </div>

                <h1 className="black-text text-2xl font-medium mb-2">Funcionalidade a caminho!</h1>

                <p className="text text-lg mb-8">Esta página ainda não foi implementada. Estamos polindo os últimos detalhes.</p>

                <Link to="/">
                    <Button className="inline-flex items-center w-full">
                        <Lu.LuArrowLeft className="w-4 h-4 mr-2" />
                        Voltar para Home
                    </Button>
                </Link>
            </Card>
        </div>
    );
}
