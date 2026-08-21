interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="flex min-h-[calc(100dvh-var(--spacing-navbar))] items-start justify-center bg-linear-to-b from-blue-100 to-neutral-25 px-4 py-6 sm:items-center sm:py-12">
      <div className="flex w-full max-w-md flex-col gap-6 rounded-2xl bg-white p-5 shadow-lg xs:p-6 md:gap-8 md:p-8">
        {children}
      </div>
    </div>
  );
}
