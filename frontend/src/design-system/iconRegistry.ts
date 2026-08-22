import type { IconType } from "react-icons";
import {
  LuArrowLeft,
  LuCheck,
  LuChevronLeft,
  LuChevronRight,
  LuCircleAlert,
  LuCircleCheck,
  LuCircleX,
  LuHammer,
  LuInfo,
  LuLoaderCircle,
  LuSearch,
  LuTriangleAlert,
  LuX,
} from "react-icons/lu";

export const systemIcons = {
  alert: LuInfo,
  back: LuArrowLeft,
  check: LuCheck,
  success: LuCircleCheck,
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

export const iconSizes = {
  sm: 16,
  md: 20,
  lg: 24,
  xl: 48,
} as const;
