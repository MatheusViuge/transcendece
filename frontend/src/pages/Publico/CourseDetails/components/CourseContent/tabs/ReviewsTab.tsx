import { FaStar } from "react-icons/fa";

// Dados simulados (Mock)
const reviewsMock = [
  {
    id: 1,
    name: "Babi Nunes",
    date: "há 2 semanas",
    rating: 5,
    comment: "O curso é excelente! A didática do professor é muito boa, consegui entender conceitos de React que eu travava antes. Recomendo demais!"
  },
  {
    id: 2,
    name: "Gabriel Vinicius",
    date: "há 1 mês",
    rating: 4,
    comment: "Conteúdo muito completo. Só achei que o módulo de CSS poderia ter mais exercícios práticos, mas de resto é perfeito."
  },
  {
    id: 3,
    name: "Guilherme Barreto",
    date: "há 3 meses",
    rating: 5,
    comment: "Melhor investimento que fiz na minha carreira esse ano. Já estou aplicando o que aprendi no meu estágio."
  }
];

export function ReviewsTab() {
  return (
    <div className="flex flex-col gap-8 py-6 max-w-4xl text-neutral-600">
      
      {/* Resumo da Nota */}
      <div className="flex items-center gap-4 border-b border-neutral-100 pb-6">
        <div className="flex flex-col">
            <span className="text-5xl font-medium text-neutral-900">4.8</span>
            <span className="text-xs text-neutral-500 font-medium">de 5.0</span>
        </div>
        <div className="flex flex-col gap-1">
            <div className="flex text-yellow text-lg">
                <FaStar /><FaStar /><FaStar /><FaStar /><FaStar />
            </div>
            <span className="text-sm text-neutral-500">(1.240 avaliações)</span>
        </div>
      </div>

      {/* Lista de Avaliações */}
      <div className="flex flex-col gap-6">
        {reviewsMock.map((review) => (
          <div key={review.id} className="flex gap-4 items-start">
            
            {/* Avatar (Iniciais) */}
            <div className="w-10 h-10 bg-neutral-100 rounded-full flex items-center justify-center text-sm font-bold text-neutral-600 shrink-0">
              {review.name.charAt(0)}
            </div>

            <div className="flex flex-col gap-1 w-full">
              {/* Nome e Data */}
              <div className="flex justify-between items-center">
                <h4 className="font-medium text-neutral-900 text-sm">{review.name}</h4>
                <span className="text-xs text-neutral-400">{review.date}</span>
              </div>

              {/* Estrelas Individuais */}
              <div className="flex text-yellowtext-xs mb-1">
                {[...Array(5)].map((_, i) => (
                    <FaStar key={i} className={i < review.rating ? "text-yellow" : "text-neutral-200"} />
                ))}
              </div>

              {/* Comentário */}
              <p className="text-sm leading-relaxed text-neutral-700">
                {review.comment}
              </p>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}