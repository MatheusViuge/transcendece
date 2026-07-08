import type { ComponentProps } from "react";
import { tv } from "tailwind-variants";
import { LuStar } from 'react-icons/lu'; 

// card para instrutor do curso
const authorStyles = tv({
  base: "text",
});

export function CardAuthor({ className, ...props }: ComponentProps<'p'>) {
  return <p className={authorStyles({ className })} {...props} />;
}

// card para avaliação do curso
const ratingStyles = tv({
  base: "flex items-center gap-1 text-sm",
});

interface CardRatingProps extends ComponentProps<'div'> {
  rating: number;  
  reviews: number; 
}

export function CardRating({ rating, reviews, className, ...props }: CardRatingProps) {
  return (
    <div className={ratingStyles({ className })} {...props}>
      <LuStar className="text-base text-yellow fill-yellow" />

      <span className="font-normal text-dark-black">{rating}</span>
      <span className="text-dark-gray">({reviews})</span>
    </div>
  );
}

// card para preço do curso
const priceStyles = tv({
  base: "font-normal text-base text-blue mt-auto",
});

interface CardPriceProps extends ComponentProps<'span'> {
  value: number; 
}

export function CardPrice({ value, className, ...props }: CardPriceProps) {
  
  const valorFormatado = !value ? "Grátis" : new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);

  return (
    <span className={priceStyles({ className })} {...props}>
      {valorFormatado}
    </span>
  );
}