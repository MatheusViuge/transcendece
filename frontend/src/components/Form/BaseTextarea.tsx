import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const styles = tv({
    base: "base-input h-35 py-2 placeholder",
});

interface IProps extends ComponentProps<"textarea">, VariantProps<typeof styles> {
    id: string;
}

export function BaseTextarea(props: IProps) {
    return (
        <textarea { ...{
            ...props,
            className: styles({ className: props.className }),
        } } />
    );
}