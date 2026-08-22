import { Badge } from "@/design-system";

type Props = {
  password: string;
};

export function PasswordStrength({ password }: Props) {
  if (!password) return null;

  const calculateStrength = (pass: string) => {
    let score = 0;
    if (pass.length >= 6) score++;
    if (/[a-zA-Z]/.test(pass)) score++;
    if (/\d/.test(pass)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(pass)) score++;
    return score;
  };

  const strength = calculateStrength(password);
  const barColor = strength <= 1 ? "bg-danger" : strength <= 3 ? "bg-warning" : "bg-success";
  const tone = strength <= 1 ? "danger" : strength <= 3 ? "warning" : "success";
  const strengthText = ["Fraca", "Média", "Forte", "Muito Forte"][Math.min(strength - 1, 3)] || "Fraca";

  return (
    <div className="mt-2">
      <div className="flex h-1 gap-1" aria-hidden="true">
        {[...Array(4)].map((_, index) => (
          <div
            key={index}
            className={`h-full flex-1 rounded-pill transition-all duration-300 ${index < strength ? barColor : "bg-neutral-200"}`}
          />
        ))}
      </div>
      <div className="mt-2 flex justify-end">
        <Badge tone={tone}>Força: {strengthText}</Badge>
      </div>
    </div>
  );
}
