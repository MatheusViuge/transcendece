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

  const getStrengthColor = () => {
    if (strength <= 1) return "bg-red-500";
    if (strength <= 3) return "bg-yellow-500";
    return "bg-green-500";
  };

  const strengthText = ["Fraca", "Média", "Forte", "Muito Forte"][Math.min(strength - 1, 3)] || "Fraca";

  return (
    <div className="mt-2">
      <div className="flex gap-1 h-1">
        {[...Array(4)].map((_, index) => (
          <div
            key={index}
            className={`h-full flex-1 rounded-full transition-all duration-300 ${
              index < strength ? getStrengthColor() : "bg-gray-200"
            }`}
          />
        ))}
      </div>
      <p className="text-xs text-gray-500 text-right mt-1">Força: {strengthText}</p>
    </div>
  );
}