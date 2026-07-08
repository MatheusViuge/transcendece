import type { ComponentProps } from "react";
import { tv } from "tailwind-variants";

const styles = tv({
    base: "grid auto-rows-auto gap-2 w-full",
    variants: {
        inline: {
            true: "grid-cols-[auto_1fr] items-center gap-x-4",
        },
    }
});

interface IPropsFormField extends ComponentProps<'div'> {
    inline?: boolean;
}

export function FormField(props: IPropsFormField) {
  return (
    <div { ...{
        ...props,
        className: styles({ className: props.className, inline: props.inline }),
        inline: undefined
    } }>
        { props.children }
    </div>
  );
}