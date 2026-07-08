import { tv } from "tailwind-variants";

const styles = tv({
    base: "text-xs text-red ml-1",
});

export function FieldError({ message="", className }: { message: string, className?: string }) {
    return (
        <span className={styles({ className })}>{ message }</span>
    );
}