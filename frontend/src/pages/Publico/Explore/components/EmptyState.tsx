interface EmptyStateProps {
  message?: string;
}

export default function EmptyState({ message = "Nenhum curso encontrado no momento." }: EmptyStateProps) {
  return (
    <div className="text-center py-20 animate-fade-in">
      {/* Ícone de pasta vazia */}
      <div className="flex justify-center mb-4">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-16 w-16 text-neutral-300" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      
      <p className="text-neutral-500 text-lg font-medium">{message}</p>
      <p className="text-neutral-400 text-sm mt-1">Tente ajustar seus filtros ou volte mais tarde.</p>
    </div>
  );
}