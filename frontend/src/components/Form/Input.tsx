import type { ComponentProps } from "react";
import { BaseInput } from "./BaseInput";
import { Label } from "./Label";
import { FormField } from "./FormField";
import { FieldError } from "./FieldError";
import type React from "react";

interface IPropsInput extends ComponentProps<typeof BaseInput> {
    label: React.ReactNode;
    errors?: Record<string, Record<string, string>>;
    classNames?: {
        formField?: string;
        label?: string;
        input?: string;
    };
}

export function Input(props: IPropsInput) {
    const inline = ["radio", "checkbox"].includes(props.type||"");

    return (
        <FormField inline={inline} className={props.classNames?.formField}>
            <Label htmlFor={props.id} className={props.classNames?.label} required={props.required}>{props.label}</Label>

            <BaseInput { ...{
                ...props,
                className: props.classNames?.input
            } } />

            { props.errors?.[props.id] && (
                <FieldError message={props.errors?.[props.id].message} />
            )}
        </FormField>
    );
}