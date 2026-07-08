import { tv } from "tailwind-variants";

export function ContainerInputs({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <div
        className={tv({ base: "grid gap-4"})({ className })}
    >{children}</div>
  );
}