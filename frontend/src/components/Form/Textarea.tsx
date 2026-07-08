import type { ComponentProps } from "react";
import { BaseTextarea } from "./BaseTextarea";
import { FormField } from "./FormField";
import { Label } from "./Label";
import { FieldError } from "./FieldError";
import type React from "react";

interface IPropsSelect extends ComponentProps<typeof BaseTextarea> {
    label: React.ReactNode;
    errors?: Record<string, Record<string, string>>;
    classNames?: {
        formField?: string;
        label?: string;
        textarea?: string;
    };
}

export function Textarea(props: IPropsSelect) {
    return (
        <FormField className={props.classNames?.formField}>
            <Label htmlFor={props.id} className={props.classNames?.label} required={props.required}>{props.label}</Label>

            <BaseTextarea { ...{
                ...props,
                className: props.classNames?.textarea,
            } } />

            { props.errors?.[props.id] && (
                <FieldError message={props.errors?.[props.id].message} />
            )}
        </FormField>
    );
}