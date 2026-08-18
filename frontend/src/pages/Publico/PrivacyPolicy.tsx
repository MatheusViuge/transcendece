import { Link } from "react-router-dom";

const LAST_UPDATED = "18 de agosto de 2026";

export default function PrivacyPolicy() {
  return (
    <article className="mx-auto w-full max-w-4xl px-4 py-10 md:px-8 md:py-14">
      <header className="mb-10 space-y-3">
        <p className="text-sm font-medium text-neutral-500">Última atualização: {LAST_UPDATED}</p>
        <h1 className="text-3xl font-semibold text-neutral-900 md:text-4xl">
          Política de Privacidade
        </h1>
        <p className="max-w-3xl text-base leading-7 text-neutral-700">
          Esta Política de Privacidade explica quais dados são tratados pela plataforma,
          por que eles são necessários e quais cuidados são adotados durante o uso do serviço.
        </p>
      </header>

      <div className="space-y-8 text-neutral-700">
        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">1. Dados que podemos coletar</h2>
          <p className="leading-7">
            Para criar e manter uma conta, podemos tratar informações fornecidas pelo próprio
            usuário, como nome, sobrenome, data de nascimento e endereço de e-mail. A senha é
            utilizada apenas para autenticação e deve ser armazenada pelo backend de forma
            protegida, nunca como texto simples.
          </p>
          <p className="leading-7">
            Também podemos registrar dados necessários ao funcionamento da plataforma, como
            informações de perfil, cursos, matrículas, progresso, avaliações e demais ações
            executadas dentro das funcionalidades efetivamente disponíveis.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">2. Finalidades do tratamento</h2>
          <p className="leading-7">Os dados são utilizados somente quando necessários para:</p>
          <ul className="list-disc space-y-2 pl-6 leading-7">
            <li>criar, autenticar e manter contas de usuário;</li>
            <li>disponibilizar recursos educacionais e registrar progresso;</li>
            <li>exibir informações de perfil e conteúdo relacionado à conta;</li>
            <li>proteger a aplicação contra uso indevido e acessos não autorizados;</li>
            <li>diagnosticar falhas técnicas sem expor credenciais ou informações sensíveis.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">3. Armazenamento e segurança</h2>
          <p className="leading-7">
            A aplicação adota controles técnicos compatíveis com seu funcionamento, incluindo
            validação de dados no frontend e no backend, proteção de credenciais, controle de
            acesso e comunicação externa com o backend por HTTPS no ambiente de entrega.
          </p>
          <p className="leading-7">
            Segredos de infraestrutura, chaves privadas e variáveis sensíveis não devem ser
            expostos no frontend, em páginas públicas ou em respostas da API.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">4. Conteúdo enviado pelo usuário</h2>
          <p className="leading-7">
            Quando uma funcionalidade permitir o envio de conteúdo ou arquivos, esses dados serão
            tratados apenas para viabilizar o recurso correspondente e estarão sujeitos às regras
            de validação, armazenamento e acesso implementadas pela plataforma.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">5. Serviços e integrações externas</h2>
          <p className="leading-7">
            Caso algum serviço externo seja utilizado no ambiente em execução, ele deverá ser
            configurado de forma compatível com esta política. Credenciais de terceiros não são
            apresentadas aos usuários nem versionadas como parte da aplicação.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">6. Acesso, correção e remoção</h2>
          <p className="leading-7">
            O usuário pode solicitar correção ou remoção de dados associados à própria conta quando
            isso for compatível com as funcionalidades e obrigações técnicas da aplicação. A
            solicitação deve ser feita pelo canal de contato disponibilizado pelo projeto.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold text-neutral-900">7. Alterações desta política</h2>
          <p className="leading-7">
            Esta página pode ser atualizada quando houver mudanças relevantes no comportamento da
            aplicação. A data exibida no início do documento indica a versão vigente.
          </p>
        </section>

        <section className="rounded-xl border border-neutral-200 bg-neutral-50 p-5">
          <h2 className="text-xl font-semibold text-neutral-900">8. Contato e documentos relacionados</h2>
          <p className="mt-3 leading-7">
            Para dúvidas sobre privacidade, utilize o canal de contato disponibilizado pela
            plataforma. As condições gerais de utilização estão descritas nos{" "}
            <Link className="font-medium underline underline-offset-4" to="/termos">
              Termos de Serviço
            </Link>
            .
          </p>
        </section>
      </div>
    </article>
  );
}
