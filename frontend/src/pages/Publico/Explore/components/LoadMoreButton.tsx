import { Button } from "@/components/Button"; 

interface LoadMoreButtonProps {
  onClick?: () => void;
}

export default function LoadMoreButton({ onClick }: LoadMoreButtonProps) {
  return (
    <div className="flex justify-center mt-12 animate-fade-in">
      <Button 
        variant="secondary" 
        onClick={onClick}>
        Carregar mais cursos
      </Button>
    </div>
  );
}