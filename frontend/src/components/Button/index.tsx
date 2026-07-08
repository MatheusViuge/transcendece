import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

// Usei o tailwind-variants pra organizar as variações de estilo de forma limpa
const buttonStyles = tv({
  base: "py-1.5 px-4 rounded-lg font-normal border border-solid transition-all duration-200 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 disabled:opacity-50 disabled:cursor-not-allowed hover:cursor-pointer",
  
  variants: {
    variant: {
      primary: "bg-neutral-900 hover:bg-gray text-white border-transparent",
      secondary: "bg-white hover:bg-neutral-200 text-neutral-900 border-black/50 hover:border-neutral-200",
      accent: "bg-blue hover:bg-blue-500 text-white border-transparent",
      badge: "bg-neutral-900 hover:bg-gray text-white text-xs px-2 py-1 border-transparent"
    },
    fullWidth: {
      true: "w-full",
      false: "w-auto",
    },
  },
  
  defaultVariants: {
    variant: "primary",
    fullWidth: false,
  },
});

// Tipagem pro TypeScript reconhecer as variantes no autocomplete
type ButtonSchema = VariantProps<typeof buttonStyles>;
interface ButtonProps extends ComponentProps<'button'>, ButtonSchema {}

export function Button({ className, variant, fullWidth, ...props }: ButtonProps) {
  return (
    <button 
      className={buttonStyles({ variant, fullWidth, className })} 
      {...props} 
    >
      {props.children}
    </button>
  );
}