import { Button } from "@/components/Button";
import { isProtectedPath } from "@/pages/Layout/protectedRoutes";
import { useLocation } from "react-router-dom";
import { styles } from "./styles";

interface HeaderPriceProps {
  price: number;
}

export function HeaderPrice({ price }: HeaderPriceProps) {
  const location = useLocation();
  const isProtectedRoute = isProtectedPath(location.pathname);
  const formattedPrice = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(price);

  return (
    <div className={styles.priceWrapper}>
      <span className={styles.priceText}>{formattedPrice}</span>

      <div className={styles.buttonContainer + (isProtectedRoute ? " hidden" : "")}>
        <Button>Começar Agora</Button>
      </div>
    </div>
  );
}
