import type { ComponentProps } from "react";
import { BaseSelect } from "./BaseSelect";
import { FormField } from "./FormField";
import { Label } from "./Label";
import { FieldError } from "./FieldError";
import type React from "react";

interface IPropsSelect extends ComponentProps<typeof BaseSelect> {
    label: React.ReactNode;
    errors?: Record<string, Record<string, string>>;
    classNames?: {
        formField?: string;
        label?: string;
        select?: string;
    };
}

export function Select(props: IPropsSelect) {
    return (
        <FormField className={props.classNames?.formField}>
            <Label htmlFor={props.id} className={props.classNames?.label} required={props.required}>{props.label}</Label>

            <BaseSelect { ...{
                ...props,
                className: props.classNames?.select,
            } } />

            { props.errors?.[props.id] && (
                <FieldError message={props.errors?.[props.id].message} />
            )}
        </FormField>
    );
}