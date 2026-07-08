import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const styles = tv({
    base: `base-input placeholder`,
    variants: {
        typeInput: {
            radio: "h-4 w-4 col-start-1 row-start-1",
            checkbox: "h-4 w-4 col-start-1 row-start-1",
        },
    },
});

interface IProps extends ComponentProps<"input">, VariantProps<typeof styles> {
    id: string;
}

export function BaseInput(props: IProps) {
    return (
        <input { ...{
            ...props,
            name: props.name ?? props.id,
            className: styles({ typeInput: props.type as IProps["typeInput"], className: props.className }),
        } } />
    );
}