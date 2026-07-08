import simbolo from "@/assets/simbolo_black.svg";

export function RegisterHeader() {
  return (
    <div className="grid gap-2 text-center">
      <div className="flex justify-center pb-4">
        <img src={simbolo} alt="Logo" className="h-12 w-auto" />
      </div>

      <h2 className="text-lg leading-6 black-text">Crie sua conta</h2>

      <p className="text">
        Comece sua jornada de aprendizado hoje!
      </p>
    </div>
  );
}