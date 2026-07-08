import { Button } from "@/components/Button"; // Ajuste o caminho se necessário
import { styles } from "./styles";
import { basedPathProtected } from "@/pages/Layout/PrivateRoute";
import { useLocation } from "react-router-dom";

interface HeaderPriceProps {
  price: number;
}

export function HeaderPrice({ price }: HeaderPriceProps) {
  const location = useLocation();
  const isProtectedRoute = basedPathProtected.some(path => location.pathname.startsWith(path));

  // Lógica de formatação isolada aqui
  const formattedPrice = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(price);

  return (
    <div className={styles.priceWrapper}>
      <span className={styles.priceText}>
        {formattedPrice}
      </span>

      <div className={styles.buttonContainer + (isProtectedRoute ? " hidden" : "")}>
        {/* Reutilizando Button e passando classes extras via className */}
        <Button>
          Começar Agora
        </Button>
      </div>
    </div>
  );
}