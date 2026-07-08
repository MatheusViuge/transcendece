interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="bg-linear-to-b from-blue-100 to-neutral-25 h-[calc(100vh-var(--spacing-navbar))] flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-6 md:p-8 flex flex-col gap-6 md:gap-8">
        {children}
      </div>
    </div>
  );
}