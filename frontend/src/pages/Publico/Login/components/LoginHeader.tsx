import { BrandLogo } from "@/brand";

export function LoginHeader() {
  return (
    <div className="flex flex-col gap-2 text-center">
      <div className="mb-4 flex justify-center">
        <BrandLogo compact className="h-12 w-auto" />
      </div>
      <h2 className="black-text text-lg leading-6">Bem vindo(a) de volta!</h2>
      <p className="text">Entre para continuar aprendendo!</p>
    </div>
  );
}
