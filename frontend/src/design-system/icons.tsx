import { iconSizes, systemIcons, type SystemIconName } from "./iconRegistry";

type IconProps = {
  name: SystemIconName;
  size?: keyof typeof iconSizes;
  className?: string;
  label?: string;
};

export function Icon({ name, size = "md", className, label }: IconProps) {
  const Component = systemIcons[name];

  return (
    <Component
      size={iconSizes[size]}
      className={className}
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? "img" : undefined}
    />
  );
}
