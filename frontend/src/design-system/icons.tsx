import type { IconType } from "react-icons";
import {
  LuAlertCircle,
  LuArrowLeft,
  LuCheck,
  LuCheckCircle2,
  LuChevronLeft,
  LuChevronRight,
  LuCircleAlert,
  LuCircleX,
  LuHammer,
  LuInfo,
  LuLoaderCircle,
  LuSearch,
  LuTriangleAlert,
  LuX,
} from "react-icons/lu";

export const systemIcons = {
  alert: LuAlertCircle,
  back: LuArrowLeft,
  check: LuCheck,
  success: LuCheckCircle2,
  previous: LuChevronLeft,
  next: LuChevronRight,
  warning: LuTriangleAlert,
  danger: LuCircleX,
  error: LuCircleAlert,
  hammer: LuHammer,
  info: LuInfo,
  loading: LuLoaderCircle,
  search: LuSearch,
  close: LuX,
} satisfies Record<string, IconType>;

export type SystemIconName = keyof typeof systemIcons;

const iconSizes = {
  sm: 16,
  md: 20,
  lg: 24,
  xl: 48,
} as const;

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
