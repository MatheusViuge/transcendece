import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const cardProgressStyles = tv({
  base: "grid gap-3",
});

type CardProgressSchema = VariantProps<typeof cardProgressStyles>;

interface CardProgressProps extends ComponentProps<'div'>, CardProgressSchema {
  progress: number;
  progressText?: string;
}

export function CardProgress({ 
  className, 
  children, 
  progress, 
  progressText, 
  ...props 
}: CardProgressProps) {
  
  const safeProgress = Math.min(100, Math.max(0, progress));

  return (
    <div className={cardProgressStyles({ className })} {...props}>
      
      <div className="flex justify-between items-center text">
        <span>Progresso</span>
        
        <span className="text-blue">
          {progressText || `${safeProgress}% Completo`}
        </span>
      </div>

      <div className="h-2 rounded-full bg-neutral-950/20">
        <div 
          className="h-full rounded-full bg-neutral-950 text transition-all duration-300" 
          style={{ width: `${safeProgress}%` }}
        />
      </div>
      
      {children}
    </div>
  );
}