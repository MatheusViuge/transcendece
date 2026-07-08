import { UserContext } from "@/Context/UserContext";
import { useContext } from "react";

export function useUser() {
  const context = useContext(UserContext);
  
  if (!context) {
    throw new Error('useUser deve ser usado dentro de UserProvider');
  }
  
  return context;
}