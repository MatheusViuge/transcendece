import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";

import { Button } from "@/components/Button";
import { BaseInput } from "@/components/Form";
import { Modal } from "@/design-system/components/Modal";
import { Pagination } from "@/design-system/components/Pagination";
import { useUser } from "@/hooks/useUser";
import { ROLE_LABELS, type UserRole } from "@/routes/access";
import { api, catchCustom } from "@/services/api";

type AdminUser = {
    id: number;
    nome: string;
    sobrenome: string;
    email: string;
    data_nascimento: string;
    tipo_usuario: UserRole;
    is_active: boolean;
    data_cadastro: string;
    ultimo_login: string | null;
};

type UserPage = {
    items: AdminUser[];
    pagination: {
        page: number;
        page_size: number;
        total: number;
        total_pages: number;
    };
};

type Specialty = { id: number; nome: string };

type FormState = {
    nome: string;
    sobrenome: string;
    email: string;
    senha: string;
    data_nascimento: string;
    role: UserRole;
    especialidade_id: string;
};

const emptyForm: FormState = {
    nome: "",
    sobrenome: "",
    email: "",
    senha: "",
    data_nascimento: "",
    role: "aluno",
    especialidade_id: "",
};

export default function AdminUsers() {
    const { user } = useUser();
    const [items, setItems] = useState<AdminUser[]>([]);
    const [specialties, setSpecialties] = useState<Specialty[]>([]);
    const [loading, setLoading] = useState(true);
    const [q, setQ] = useState("");
    const [role, setRole] = useState<"" | UserRole>("");
    const [active, setActive] = useState<"" | "true" | "false">("");
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [modalOpen, setModalOpen] = useState(false);
    const [editing, setEditing] = useState<AdminUser | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);

    const queryString = useMemo(() => {
        const params = new URLSearchParams({ page: String(page), page_size: "10" });
        if (q.trim()) params.set("q", q.trim());
        if (role) params.set("role", role);
        if (active) params.set("active", active);
        return params.toString();
    }, [active, page, q, role]);

    const loadUsers = useCallback(async () => {
        setLoading(true);
        try {
            const response = await api.get<UserPage>({
                url: `/admin/users?${queryString}`,
                hiddenToast: true,
            });
            setItems(response.data.items);
            setTotal(response.data.pagination.total);
            setTotalPages(response.data.pagination.total_pages);
        } catch (error) {
            catchCustom(error);
        } finally {
            setLoading(false);
        }
    }, [queryString]);

    useEffect(() => {
        void loadUsers();
    }, [loadUsers]);

    useEffect(() => {
        void api.get<Specialty[]>({ url: "/admin/specialties", hiddenToast: true })
            .then((response) => setSpecialties(response.data))
            .catch((error) => catchCustom(error));
    }, []);

    const openCreate = () => {
        setEditing(null);
        setForm(emptyForm);
        setModalOpen(true);
    };

    const openEdit = (target: AdminUser) => {
        setEditing(target);
        setForm({
            nome: target.nome,
            sobrenome: target.sobrenome,
            email: target.email,
            senha: "",
            data_nascimento: target.data_nascimento,
            role: target.tipo_usuario,
            especialidade_id: "",
        });
        setModalOpen(true);
    };

    const submitUser = async (event: FormEvent) => {
        event.preventDefault();
        try {
            if (editing) {
                await api.patch({
                    url: `/admin/users/${editing.id}`,
                    body: {
                        nome: form.nome,
                        sobrenome: form.sobrenome,
                        email: form.email,
                        data_nascimento: form.data_nascimento,
                    },
                });
            } else {
                await api.post({
                    url: "/admin/users",
                    body: {
                        nome: form.nome,
                        sobrenome: form.sobrenome,
                        email: form.email,
                        senha: form.senha,
                        data_nascimento: form.data_nascimento,
                        role: form.role,
                        especialidade_id: form.role === "instrutor" ? Number(form.especialidade_id) : null,
                    },
                });
            }
            setModalOpen(false);
            await loadUsers();
        } catch (error) {
            catchCustom(error);
        }
    };

    const changeRole = async (target: AdminUser, nextRole: UserRole) => {
        if (target.tipo_usuario === nextRole) return;
        if (!window.confirm(`Alterar ${target.nome} de ${ROLE_LABELS[target.tipo_usuario]} para ${ROLE_LABELS[nextRole]}?`)) return;

        const specialtyId = nextRole === "instrutor" ? specialties[0]?.id : undefined;
        if (nextRole === "instrutor" && !specialtyId) {
            catchCustom(new Error("Nenhuma especialidade disponível para promover este usuário a instrutor."));
            return;
        }

        try {
            await api.patch({
                url: `/admin/users/${target.id}/role`,
                body: {
                    role: nextRole,
                    especialidade_id: specialtyId ?? null,
                },
            });
            await loadUsers();
        } catch (error) {
            catchCustom(error);
        }
    };

    const toggleActive = async (target: AdminUser) => {
        const next = !target.is_active;
        if (!window.confirm(`${next ? "Reativar" : "Desativar"} ${target.nome} ${target.sobrenome}?`)) return;
        try {
            await api.patch({
                url: `/admin/users/${target.id}/status`,
                body: { is_active: next },
            });
            await loadUsers();
        } catch (error) {
            catchCustom(error);
        }
    };

    return (
        <section className="mx-auto w-full max-w-7xl px-4 py-8 md:px-8">
            <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                <div>
                    <p className="text-sm font-semibold uppercase tracking-wide text-text-muted">Administração</p>
                    <h1 className="text-3xl font-semibold text-text">Usuários e roles</h1>
                    <p className="mt-2 text-sm text-text-muted">{total} usuário(s). O backend continua sendo a fonte final de autorização.</p>
                </div>
                <Button type="button" onClick={openCreate}>Criar usuário</Button>
            </div>

            <div className="mb-5 grid gap-3 rounded-card border border-border bg-surface p-4 md:grid-cols-3">
                <label className="grid gap-1 text-sm font-medium text-text">
                    Buscar
                    <BaseInput
                        id="admin-user-search"
                        value={q}
                        onChange={(event) => { setQ(event.target.value); setPage(1); }}
                        placeholder="Nome ou email"
                    />
                </label>
                <label className="grid gap-1 text-sm font-medium text-text">
                    Role
                    <select
                        className="base-input"
                        value={role}
                        onChange={(event) => { setRole(event.target.value as "" | UserRole); setPage(1); }}
                    >
                        <option value="">Todas</option>
                        <option value="aluno">Aluno</option>
                        <option value="instrutor">Instrutor</option>
                        <option value="admin">Administrador</option>
                    </select>
                </label>
                <label className="grid gap-1 text-sm font-medium text-text">
                    Status
                    <select
                        className="base-input"
                        value={active}
                        onChange={(event) => { setActive(event.target.value as typeof active); setPage(1); }}
                    >
                        <option value="">Todos</option>
                        <option value="true">Ativos</option>
                        <option value="false">Desativados</option>
                    </select>
                </label>
            </div>

            <div className="overflow-x-auto rounded-card border border-border bg-surface">
                <table className="min-w-[920px] w-full border-collapse text-left text-sm">
                    <thead className="bg-surface-muted text-text-muted">
                        <tr>
                            <th className="px-4 py-3">Usuário</th>
                            <th className="px-4 py-3">Email</th>
                            <th className="px-4 py-3">Role</th>
                            <th className="px-4 py-3">Status</th>
                            <th className="px-4 py-3">Último login</th>
                            <th className="px-4 py-3 text-right">Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td className="px-4 py-8 text-center text-text-muted" colSpan={6}>Carregando usuários...</td></tr>
                        ) : items.length === 0 ? (
                            <tr><td className="px-4 py-8 text-center text-text-muted" colSpan={6}>Nenhum usuário encontrado.</td></tr>
                        ) : items.map((target) => {
                            const isSelf = target.id === user?.id;
                            return (
                                <tr key={target.id} className="border-t border-border align-middle">
                                    <td className="px-4 py-3 font-medium text-text">{target.nome} {target.sobrenome}{isSelf ? " (você)" : ""}</td>
                                    <td className="px-4 py-3 text-text-muted">{target.email}</td>
                                    <td className="px-4 py-3">
                                        <select
                                            aria-label={`Role de ${target.nome}`}
                                            className="base-input min-w-36"
                                            value={target.tipo_usuario}
                                            disabled={isSelf}
                                            onChange={(event) => void changeRole(target, event.target.value as UserRole)}
                                        >
                                            <option value="aluno">Aluno</option>
                                            <option value="instrutor">Instrutor</option>
                                            <option value="admin">Administrador</option>
                                        </select>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={target.is_active ? "font-medium text-success" : "font-medium text-danger"}>
                                            {target.is_active ? "Ativo" : "Desativado"}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-text-muted">
                                        {target.ultimo_login ? new Date(target.ultimo_login).toLocaleString("pt-BR") : "Nunca"}
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex justify-end gap-2">
                                            <Button type="button" variant="secondary" onClick={() => openEdit(target)}>Editar</Button>
                                            <Button
                                                type="button"
                                                variant="secondary"
                                                disabled={isSelf}
                                                onClick={() => void toggleActive(target)}
                                            >
                                                {target.is_active ? "Desativar" : "Reativar"}
                                            </Button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            <div className="mt-5 flex justify-end">
                <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
            </div>

            <Modal
                open={modalOpen}
                title={editing ? "Editar usuário" : "Criar usuário"}
                description={editing ? "Dados administrativos sem exposição de senha ou secrets." : "A criação administrativa exige uma senha inicial forte."}
                onClose={() => setModalOpen(false)}
            >
                <form className="grid gap-4" onSubmit={submitUser}>
                    <div className="grid gap-3 sm:grid-cols-2">
                        <label className="grid gap-1 text-sm font-medium">Nome
                            <BaseInput id="admin-name" required value={form.nome} onChange={(event) => setForm((value) => ({ ...value, nome: event.target.value }))} />
                        </label>
                        <label className="grid gap-1 text-sm font-medium">Sobrenome
                            <BaseInput id="admin-lastname" required value={form.sobrenome} onChange={(event) => setForm((value) => ({ ...value, sobrenome: event.target.value }))} />
                        </label>
                    </div>
                    <label className="grid gap-1 text-sm font-medium">Email
                        <BaseInput id="admin-email" type="email" required value={form.email} onChange={(event) => setForm((value) => ({ ...value, email: event.target.value }))} />
                    </label>
                    <label className="grid gap-1 text-sm font-medium">Data de nascimento
                        <BaseInput id="admin-birth" type="date" required value={form.data_nascimento} onChange={(event) => setForm((value) => ({ ...value, data_nascimento: event.target.value }))} />
                    </label>
                    {!editing && (
                        <>
                            <label className="grid gap-1 text-sm font-medium">Senha inicial
                                <BaseInput id="admin-password" type="password" required value={form.senha} onChange={(event) => setForm((value) => ({ ...value, senha: event.target.value }))} />
                            </label>
                            <label className="grid gap-1 text-sm font-medium">Role inicial
                                <select className="base-input" value={form.role} onChange={(event) => setForm((value) => ({ ...value, role: event.target.value as UserRole }))}>
                                    <option value="aluno">Aluno</option>
                                    <option value="instrutor">Instrutor</option>
                                    <option value="admin">Administrador</option>
                                </select>
                            </label>
                            {form.role === "instrutor" && (
                                <label className="grid gap-1 text-sm font-medium">Especialidade
                                    <select
                                        className="base-input"
                                        required
                                        value={form.especialidade_id}
                                        onChange={(event) => setForm((value) => ({ ...value, especialidade_id: event.target.value }))}
                                    >
                                        <option value="">Selecione</option>
                                        {specialties.map((specialty) => <option key={specialty.id} value={specialty.id}>{specialty.nome}</option>)}
                                    </select>
                                </label>
                            )}
                        </>
                    )}
                    <div className="flex justify-end gap-2 pt-2">
                        <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancelar</Button>
                        <Button type="submit">{editing ? "Salvar" : "Criar usuário"}</Button>
                    </div>
                </form>
            </Modal>
        </section>
    );
}
