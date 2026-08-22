import hero from "@/assets/fotoheader.jpg";
import logoOnDark from "@/assets/logo_white.svg";
import logoOnLight from "@/assets/logo_black.svg";
import symbolOnDark from "@/assets/simbolo_white.svg";
import symbolOnLight from "@/assets/simbolo_black.svg";

/**
 * Single asset mapping for the current visual identity.
 *
 * Rebranding rule: application components must not import brand image files
 * directly. Replace the physical files and/or this mapping instead.
 */
export const brandAssets = {
  wordmark: {
    onLight: logoOnLight,
    onDark: logoOnDark,
  },
  symbol: {
    onLight: symbolOnLight,
    onDark: symbolOnDark,
  },
  imagery: {
    hero,
  },
} as const;
