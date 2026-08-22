import type { ComponentProps } from "react";
import { brandAssets } from "./assets";
import { brandIdentity } from "./identity";

type BrandLogoProps = Omit<ComponentProps<"img">, "src" | "alt"> & {
  compact?: boolean;
  surface?: "light" | "dark";
  alt?: string;
};

export function BrandLogo({
  compact = false,
  surface = "light",
  alt = brandIdentity.name,
  ...props
}: BrandLogoProps) {
  const variant = surface === "dark" ? "onDark" : "onLight";
  const src = compact
    ? brandAssets.symbol[variant]
    : brandAssets.wordmark[variant];

  return <img src={src} alt={alt} {...props} />;
}
