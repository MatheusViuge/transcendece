import { useState } from "react";
import { BrandLogo, brandIdentity } from "@/brand";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input, Select, Textarea } from "@/components/Form";
import {
  Alert,
  Badge,
  EmptyState,
  Icon,
  Modal,
  Pagination,
  Spinner,
  designTokens,
} from "@/design-system";
import { designSystemInventory } from "@/design-system/inventory";

export default function DesignSystem() {
  const [modalOpen, setModalOpen] = useState(false);
  const [page, setPage] = useState(2);

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-col gap-12 px-4 py-10 md:px-8">
      <header className="flex flex-col gap-4 border-b border-border pb-8">
        <Badge tone="primary">Custom-made Design System · 1 pt</Badge>
        <h1 className="text-4xl font-bold text-text">Sistema visual de {brandIdentity.shortName}</h1>
        <p className="max-w-3xl text-text-muted">
          Foundations, identidade desacoplada, iconografia e componentes próprios usados pela aplicação.
          Esta página é uma galeria de avaliação, não uma biblioteca externa de UI.
        </p>
      </header>

      <section className="grid gap-6" aria-labelledby="brand-heading">
        <h2 id="brand-heading" className="text-2xl font-semibold text-text">Identidade desacoplada</h2>
        <Card interactive={false} className="grid gap-6 p-6 md:grid-cols-2">
          <div className="flex min-h-32 items-center justify-center rounded-card border border-border bg-surface p-6">
            <BrandLogo className="max-h-12 max-w-full" />
          </div>
          <div className="flex min-h-32 items-center justify-center rounded-card bg-text p-6">
            <BrandLogo surface="dark" className="max-h-12 max-w-full" />
          </div>
          <p className="text-sm text-text-muted md:col-span-2">
            Componentes consomem a fachada <code>brand/</code>. Logo, símbolo, hero e textos de identidade podem ser trocados sem alterar Navbar, Footer ou Hero.
          </p>
        </Card>
      </section>

      <section className="grid gap-6" aria-labelledby="colors-heading">
        <div>
          <h2 id="colors-heading" className="text-2xl font-semibold text-text">Paleta semântica</h2>
          <p className="mt-1 text-sm text-text-muted">Tokens descrevem função, não o nome físico da cor.</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries(designTokens.colors).map(([name, value]) => (
            <div key={name} className="overflow-hidden rounded-card border border-border bg-surface">
              <div className="h-20" style={{ backgroundColor: value }} />
              <div className="p-3 text-sm">
                <strong className="block text-text">{name}</strong>
                <span className="text-text-muted">{value}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-5" aria-labelledby="type-heading">
        <h2 id="type-heading" className="text-2xl font-semibold text-text">Tipografia</h2>
        <Card interactive={false} className="space-y-4 p-6">
          <p className="text-4xl font-bold">Heading · Arimo 700</p>
          <p className="text-base">Body · Arimo 400 · 16/24</p>
          <p className="text-sm text-text-muted">Small · Arimo 400 · 14/20</p>
        </Card>
      </section>

      <section className="grid gap-6" aria-labelledby="components-heading">
        <div>
          <h2 id="components-heading" className="text-2xl font-semibold text-text">Componentes e variants</h2>
          <p className="mt-1 text-sm text-text-muted">Estados de foco, disabled, loading e semântica são centralizados.</p>
        </div>

        <Card interactive={false} className="space-y-5 p-6">
          <h3 className="font-semibold text-text">Button</h3>
          <div className="flex flex-wrap gap-3">
            <Button>Primary</Button>
            <Button variant="accent">Accent</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="danger">Danger</Button>
            <Button variant="ghost">Ghost</Button>
            <Button loading>Loading</Button>
            <Button disabled>Disabled</Button>
          </div>
        </Card>

        <Card interactive={false} className="space-y-5 p-6">
          <h3 className="font-semibold text-text">Form controls</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <Input id="ds-name" label="Input" placeholder="Digite um valor" />
            <Select
              id="ds-select"
              label="Select"
              options={[
                { value: "one", label: "Opção um" },
                { value: "two", label: "Opção dois" },
              ]}
            />
            <Textarea id="ds-textarea" label="Textarea" placeholder="Conteúdo maior" classNames={{ formField: "md:col-span-2" }} />
          </div>
        </Card>

        <Card interactive={false} className="space-y-5 p-6">
          <h3 className="font-semibold text-text">Badge + feedback</h3>
          <div className="flex flex-wrap gap-2">
            <Badge>Neutral</Badge>
            <Badge tone="primary">Primary</Badge>
            <Badge tone="success">Success</Badge>
            <Badge tone="warning">Warning</Badge>
            <Badge tone="danger">Danger</Badge>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <Alert title="Informação">Mensagem informativa reutilizável.</Alert>
            <Alert tone="success" title="Sucesso">Operação concluída.</Alert>
            <Alert tone="warning" title="Atenção">Revise os dados informados.</Alert>
            <Alert tone="danger" title="Erro">A operação não pôde ser concluída.</Alert>
          </div>
        </Card>

        <Card interactive={false} className="space-y-5 p-6">
          <h3 className="font-semibold text-text">Icons + loading + pagination</h3>
          <div className="flex flex-wrap items-center gap-5 text-primary">
            <Icon name="search" label="Busca" />
            <Icon name="success" label="Sucesso" />
            <Icon name="warning" label="Aviso" />
            <Icon name="danger" label="Erro" />
            <Spinner label="Carregando demonstração" />
          </div>
          <Pagination page={page} totalPages={5} onPageChange={setPage} />
        </Card>

        <Card interactive={false} className="space-y-5 p-6">
          <h3 className="font-semibold text-text">Modal</h3>
          <Button variant="secondary" onClick={() => setModalOpen(true)}>Abrir modal acessível</Button>
          <Modal
            open={modalOpen}
            onClose={() => setModalOpen(false)}
            title="Modal do Design System"
            description="Pode ser fechado pelo botão, clique no backdrop ou tecla Escape."
          >
            <Alert tone="info">O diálogo usa role, aria-modal e relações de título/descrição.</Alert>
          </Modal>
        </Card>

        <Card interactive={false} className="p-6">
          <EmptyState
            icon="search"
            title="Empty state reutilizável"
            description="O mesmo primitive é usado nas telas de 404 e funcionalidade em construção."
            action={<Button variant="secondary">Ação contextual</Button>}
          />
        </Card>
      </section>

      <section className="grid gap-5" aria-labelledby="inventory-heading">
        <div>
          <h2 id="inventory-heading" className="text-2xl font-semibold text-text">Inventário verificável</h2>
          <p className="mt-1 text-sm text-text-muted">{designSystemInventory.length} componentes próprios formalizados.</p>
        </div>
        <div className="overflow-x-auto rounded-card border border-border">
          <table className="w-full min-w-[680px] border-collapse text-left text-sm">
            <thead className="bg-surface-muted text-text">
              <tr>
                <th className="p-3">Componente</th>
                <th className="p-3">Fonte</th>
                <th className="p-3">Uso</th>
              </tr>
            </thead>
            <tbody>
              {designSystemInventory.map((item) => (
                <tr key={item.component} className="border-t border-border">
                  <td className="p-3 font-semibold text-text">{item.component}</td>
                  <td className="p-3 font-mono text-xs text-primary">{item.source}</td>
                  <td className="p-3 text-text-muted">{item.usage}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
