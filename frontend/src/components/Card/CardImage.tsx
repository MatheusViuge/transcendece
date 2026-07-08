import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const cardImageStyles = tv({
  base: "w-full h-56 object-cover rounded-t-lg",
});

type CardImageSchema = VariantProps<typeof cardImageStyles>;

interface CardImageProps extends ComponentProps<'img'>, CardImageSchema {
  src: string;
  alt: string;
}

export function CardImage({ className, ...props }: CardImageProps) {
  return (
    <img 
      className={cardImageStyles({ className })} 
      {...props}
    />
  );
}
