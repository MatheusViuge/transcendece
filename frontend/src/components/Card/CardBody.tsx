import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const cardBodyStyles = tv({
  base: "grid gap-2 p-4 pb-8",
});

type CardBodySchema = VariantProps<typeof cardBodyStyles>;

interface CardBodyProps extends ComponentProps<'div'>, CardBodySchema {}

export function CardBody({ className, children, ...props }: CardBodyProps) {
  return (
    <div className={cardBodyStyles({ className })} {...props}>
      {children}
    </div>
  );
}