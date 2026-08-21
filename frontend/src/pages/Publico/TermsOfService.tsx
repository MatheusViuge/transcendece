import { Link } from "react-router-dom";

const LAST_UPDATED = "18 de agosto de 2026";

export default function TermsOfService() {
  return (
    <article className="mx-auto w-full max-w-4xl px-4 py-10 md:px-8 md:py-14">
      <header className="mb-10 space-y-3">
        <p className="text-sm font-medium text-neutral-500">Última atualização: {LAST_UPDATED}</p>
        <h1 className="text-3xl font-semibold text-neutral-900 md:text-4xl">Termos de Serviço</h1>
        <p className="max-w-3xl text-base leading-7 text-neutral-700">
          Estes Termos estabelecem as condições de uso da plataforma e as responsabilidades básicas
          de quem utiliza os recursos educacionais disponibilizados pelo projeto.
        </p>
      </header>

      <div className="space-y-8 text-neutral-700">
        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">1. Uso da plataforma</h2>
          <p className="leading-7">
            A plataforma deve ser utilizada para acesso aos recursos educacionais e demais
            funcionalidades efetivamente disponibilizadas. O usuário deve utilizar o serviço de
            forma compatível com a finalidade do projeto e com estes Termos.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">2. Conta e credenciais</h2>
          <p className="leading-7">
            O usuário é responsável por fornecer dados válidos no cadastro e por manter suas
            credenciais sob controle. Não é permitido compartilhar credenciais com o objetivo de
            contornar regras de acesso, permissões ou restrições da aplicação.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">3. Responsabilidades do usuário</h2>
          <ul className="list-disc space-y-2 pl-6 leading-7">
            <li>não tentar acessar dados ou recursos de outros usuários sem autorização;</li>
            <li>não interferir no funcionamento da aplicação ou explorar falhas intencionalmente;</li>
            <li>não enviar conteúdo ilegal, ofensivo ou incompatível com a finalidade da plataforma;</li>
            <li>respeitar regras de acesso associadas ao perfil e às funcionalidades disponíveis.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">4. Conteúdo enviado</h2>
          <p className="leading-7">
            Quando a plataforma permitir envio de conteúdo, o usuário continua responsável pelo
            material enviado e deve possuir autorização para utilizá-lo. A aplicação pode rejeitar
            ou remover conteúdo incompatível com seus limites técnicos ou regras de uso.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">5. Recursos educacionais</h2>
          <p className="leading-7">
            Cursos, aulas, progresso e demais recursos educacionais são disponibilizados conforme o
            estado atual da aplicação. Funcionalidades em desenvolvimento não são consideradas parte
            do serviço até que estejam efetivamente entregues.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">6. Disponibilidade e limitações</h2>
          <p className="leading-7">
            O projeto pode passar por manutenção, atualizações ou indisponibilidade técnica. O time
            busca manter o funcionamento previsível, mas não garante disponibilidade ininterrupta em
            ambientes acadêmicos, de desenvolvimento ou demonstração.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">7. Suspensão ou encerramento de acesso</h2>
          <p className="leading-7">
            Contas podem ter acesso restringido quando houver violação das regras da plataforma,
            tentativa de acesso indevido ou necessidade administrativa compatível com as funções
            implementadas no sistema.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">8. Privacidade</h2>
          <p className="leading-7">
            O tratamento de dados pessoais e informações de conta é descrito na{" "}
            <Link className="font-medium underline underline-offset-4" to="/privacidade">
              Política de Privacidade
            </Link>
            .
          </p>
        </section>

        <section className="rounded-xl border border-neutral-200 bg-neutral-50 p-5">
          <h2 className="text-xl font-semibold text-neutral-900">9. Contato e alterações</h2>
          <p className="mt-3 leading-7">
            Dúvidas sobre estes Termos podem ser encaminhadas pelo canal de contato da plataforma.
            Alterações relevantes serão refletidas nesta página, junto da data de atualização.
          </p>
        </section>
      </div>
    </article>
  );
}
