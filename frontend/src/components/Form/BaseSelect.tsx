import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const styles = tv({
    base: "base-input placeholder",
});

interface IProps extends ComponentProps<"select">, VariantProps<typeof styles> {
    id: string;
    options: {
        value: string;
        label: string;
    }[];
}

export function BaseSelect(props: IProps) {
    return (
        <select { ...{
            ...props,
            name: props.name ?? props.id,
            className: styles({ className: props.className }),
        } }>
            <option value={undefined}>Selecione</option>
            { props.options.map((option) => (
                <option key={ option.value } value={ option.value }>{ option.label }</option>
            )) }
        </select>
    );
}