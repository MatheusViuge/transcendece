export const designTokens = {
  colors: {
    primary: "#155DFC",
    primaryHover: "#0F4BD8",
    primarySoft: "#EFF6FF",
    success: "#08783E",
    successSoft: "#ECFDF3",
    warning: "#A15C00",
    warningSoft: "#FFF7D6",
    danger: "#C1121F",
    dangerSoft: "#FFF0F1",
    surface: "#FFFFFF",
    surfaceSubtle: "#F9FAFB",
    text: "#0A0A0A",
    textMuted: "#4A5565",
    border: "#DEDEDE",
  },
  typography: {
    family: "Arimo, ui-sans-serif, system-ui, sans-serif",
    body: "16px / 24px / 400",
    small: "14px / 20px / 400",
    heading: "42px / 42px / 700",
  },
  radius: {
    control: "8px",
    card: "12px",
    pill: "9999px",
  },
  breakpoints: {
    xs: "480px",
  },
} as const;

export type DesignTokens = typeof designTokens;
