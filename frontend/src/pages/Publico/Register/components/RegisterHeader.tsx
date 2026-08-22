import { BrandLogo } from "@/brand";

export function RegisterHeader() {
  return (
    <div className="grid gap-2 text-center">
      <div className="flex justify-center pb-4">
        <BrandLogo compact className="h-12 w-auto" />
      </div>
      <h2 className="black-text text-lg leading-6">Crie sua conta</h2>
      <p className="text">Comece sua jornada de aprendizado hoje!</p>
    </div>
  );
}
