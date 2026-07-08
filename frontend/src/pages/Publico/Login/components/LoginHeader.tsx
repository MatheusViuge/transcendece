import simbolo from "@/assets/simbolo_black.svg";

export function LoginHeader() {
  return (
    <div className="text-center flex flex-col gap-2">
      <div className="flex justify-center mb-4">
        <img src={simbolo} alt="Logo" className="h-12 w-auto" />
      </div>
      <h2 className="text-lg leading-6 black-text">Bem vindo(a) de volta!</h2>
      <p className="text">
        Entre para continuar aprendendo!
      </p>
    </div>
  );
}