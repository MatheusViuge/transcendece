import { brandAssets, brandIdentity } from "@/brand";
import { Button } from "@/components/Button";

export default function Hero() {
  return (
    <header className="relative grid h-fit min-h-[400px] max-h-[600px] w-full overflow-hidden bg-linear-to-b from-primary-soft to-surface">
      <img
        className="relative inset-0 hidden bg-cover bg-[center_20%] bg-no-repeat sm:block sm:bg-[center_40%] md:bg-center"
        src={brandAssets.imagery.hero}
        alt=""
        aria-hidden="true"
      />

      <div className="absolute inset-0 sm:bg-surface/70" />

      <div className="z-20 grid h-full w-full content-center justify-center gap-6 p-4 pt-8 sm:absolute sm:inset-0 md:content-start md:justify-start md:p-[114.5px]">
        <h1 className="text-[40px] font-bold leading-none text-text xs:text-[42px]">
          {brandIdentity.hero.line1}<br />
          {brandIdentity.hero.line2}<br />
          <span className="text-primary">{brandIdentity.hero.accent}</span>
        </h1>

        <p className="max-w-[404px] text-[17.5px] leading-7 text-text-muted">
          {brandIdentity.hero.description}
        </p>

        <Button variant="accent" className="w-fit">{brandIdentity.hero.cta}</Button>
      </div>
    </header>
  );
}
