import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useUser } from "@/hooks/useUser";
import { apiConfig } from "@/services/api/apiConfig";

type Participant = {
    id: number;
    nome: string;
    sobrenome: string;
    tipo_usuario: "aluno" | "instrutor" | "admin";
    avatar_url: string;
    online: boolean | null;
    active: boolean;
};

type ChatMessage = {
    id: number;
    conversation_id: number;
    sender_id: number;
    content: string;
    created_at: string;
    event: "chat.message.created";
};

type Conversation = {
    id: number;
    participant: Participant;
    created_at: string;
    updated_at: string;
    last_message: ChatMessage | null;
};

type MessagePage = {
    items: ChatMessage[];
    has_more: boolean;
    next_before_id: number | null;
};

function messageFromError(error: unknown, fallback: string) {
    if (typeof error === "object" && error !== null && "response" in error) {
        const response = (error as { response?: { data?: { detail?: string; message?: string } } }).response;
        return response?.data?.detail || response?.data?.message || fallback;
    }
    return fallback;
}

function presenceLabel(value: boolean | null) {
    if (value === null) return "Presença privada";
    return value ? "Online" : "Offline";
}

export default function Chat() {
    const { user } = useUser();
    const [searchParams, setSearchParams] = useSearchParams();
    const recipientId = Number(searchParams.get("user") ?? 0);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [selectedId, setSelectedId] = useState<number | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [nextBeforeId, setNextBeforeId] = useState<number | null>(null);
    const [hasMore, setHasMore] = useState(false);
    const [loading, setLoading] = useState(true);
    const [messagesLoading, setMessagesLoading] = useState(false);
    const [sending, setSending] = useState(false);
    const [draft, setDraft] = useState("");
    const [error, setError] = useState<string | null>(null);

    const selected = useMemo(
        () => conversations.find((conversation) => conversation.id === selectedId) ?? null,
        [conversations, selectedId],
    );

    async function fetchConversations(preferredId?: number) {
        const response = await apiConfig().get("/chat/conversations", { params: { limit: 100 } });
        const items: Conversation[] = response.data.data.items ?? [];
        setConversations(items);
        setSelectedId((current) => {
            if (preferredId && items.some((item) => item.id === preferredId)) return preferredId;
            if (current && items.some((item) => item.id === current)) return current;
            return items[0]?.id ?? null;
        });
        return items;
    }

    useEffect(() => {
        let active = true;
        setLoading(true);
        setError(null);
        const initialize = async () => {
            try {
                let preferredId: number | undefined;
                if (Number.isInteger(recipientId) && recipientId > 0 && recipientId !== user?.id) {
                    const created = await apiConfig().post("/chat/conversations", { recipient_id: recipientId });
                    preferredId = created.data.data.id;
                    setSearchParams({}, { replace: true });
                }
                if (!active) return;
                await fetchConversations(preferredId);
            } catch (err) {
                if (active) setError(messageFromError(err, "Não foi possível carregar suas conversas."));
            } finally {
                if (active) setLoading(false);
            }
        };
        void initialize();
        return () => { active = false; };
    }, [recipientId, setSearchParams, user?.id]);

    useEffect(() => {
        if (!selectedId) {
            setMessages([]);
            setHasMore(false);
            setNextBeforeId(null);
            return;
        }
        let active = true;
        setMessagesLoading(true);
        setError(null);
        apiConfig().get(`/chat/conversations/${selectedId}/messages`, { params: { limit: 30 } })
            .then((response) => {
                if (!active) return;
                const page: MessagePage = response.data.data;
                setMessages(page.items ?? []);
                setHasMore(page.has_more);
                setNextBeforeId(page.next_before_id);
            })
            .catch((err) => active && setError(messageFromError(err, "Não foi possível carregar o histórico.")))
            .finally(() => active && setMessagesLoading(false));
        return () => { active = false; };
    }, [selectedId]);

    async function loadOlder() {
        if (!selectedId || !hasMore || !nextBeforeId || messagesLoading) return;
        setMessagesLoading(true);
        try {
            const response = await apiConfig().get(`/chat/conversations/${selectedId}/messages`, {
                params: { limit: 30, before_id: nextBeforeId },
            });
            const page: MessagePage = response.data.data;
            setMessages((current) => [...(page.items ?? []), ...current]);
            setHasMore(page.has_more);
            setNextBeforeId(page.next_before_id);
        } catch (err) {
            setError(messageFromError(err, "Não foi possível carregar mensagens anteriores."));
        } finally {
            setMessagesLoading(false);
        }
    }

    async function sendMessage(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const content = draft.trim();
        if (!selectedId || !content || sending) return;
        if (content.length > 2000) {
            setError("A mensagem deve ter no máximo 2000 caracteres.");
            return;
        }
        setSending(true);
        setError(null);
        try {
            const response = await apiConfig().post(`/chat/conversations/${selectedId}/messages`, { content });
            const sent: ChatMessage = response.data.data;
            setMessages((current) => [...current, sent]);
            setDraft("");
            await fetchConversations(selectedId);
        } catch (err) {
            setError(messageFromError(err, "Não foi possível enviar a mensagem. Tente novamente."));
        } finally {
            setSending(false);
        }
    }

    async function refreshSelected() {
        if (!selectedId) return;
        setMessagesLoading(true);
        try {
            const response = await apiConfig().get(`/chat/conversations/${selectedId}/messages`, { params: { limit: 30 } });
            const page: MessagePage = response.data.data;
            setMessages(page.items ?? []);
            setHasMore(page.has_more);
            setNextBeforeId(page.next_before_id);
            await fetchConversations(selectedId);
            setError(null);
        } catch (err) {
            setError(messageFromError(err, "Não foi possível atualizar a conversa."));
        } finally {
            setMessagesLoading(false);
        }
    }

    if (loading) return <section className="mx-auto max-w-6xl px-4 py-10 text-text-muted">Carregando conversas...</section>;

    return (
        <section className="mx-auto w-full max-w-6xl px-4 py-8 md:px-8">
            <div className="mb-6">
                <p className="text-sm font-semibold uppercase tracking-wide text-primary">Interações</p>
                <h1 className="text-3xl font-bold text-text">Chat</h1>
                <p className="mt-1 text-sm text-text-muted">Mensagens persistentes entre usuários. Atualizações em tempo real entram no módulo WebSockets.</p>
            </div>

            {error && <p role="alert" className="mb-4 rounded-card border border-danger p-3 text-danger">{error}</p>}

            <div className="grid min-h-[620px] gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
                <Card className="overflow-hidden p-0">
                    <div className="border-b border-border p-4">
                        <h2 className="font-semibold">Conversas</h2>
                    </div>
                    {conversations.length === 0 ? (
                        <div className="p-5 text-sm text-text-muted">
                            <p>Nenhuma conversa ainda.</p>
                            <p className="mt-2">Abra o perfil de outro usuário e escolha “Conversar”.</p>
                        </div>
                    ) : (
                        <ul className="max-h-[620px] overflow-y-auto">
                            {conversations.map((conversation) => {
                                const isSelected = conversation.id === selectedId;
                                return (
                                    <li key={conversation.id} className="border-b border-border last:border-0">
                                        <button
                                            type="button"
                                            onClick={() => setSelectedId(conversation.id)}
                                            className={`flex w-full items-center gap-3 p-4 text-left transition ${isSelected ? "bg-surface-muted" : "hover:bg-surface-muted"}`}
                                            aria-current={isSelected ? "true" : undefined}
                                        >
                                            <img src={conversation.participant.avatar_url} alt="" className="h-12 w-12 shrink-0 rounded-full object-cover" />
                                            <span className="min-w-0 flex-1">
                                                <strong className="block truncate">{conversation.participant.nome} {conversation.participant.sobrenome}</strong>
                                                <span className="block truncate text-xs text-text-muted">
                                                    {conversation.last_message?.content ?? "Conversa iniciada"}
                                                </span>
                                            </span>
                                            <span className="text-xs text-text-muted" aria-label={presenceLabel(conversation.participant.online)}>
                                                {conversation.participant.online === null ? "—" : conversation.participant.online ? "●" : "○"}
                                            </span>
                                        </button>
                                    </li>
                                );
                            })}
                        </ul>
                    )}
                </Card>

                <Card className="flex min-h-[620px] min-w-0 flex-col p-0">
                    {!selected ? (
                        <div className="m-auto px-6 text-center text-text-muted">Selecione uma conversa para abrir o histórico.</div>
                    ) : (
                        <>
                            <header className="flex items-center justify-between gap-3 border-b border-border p-4">
                                <Link to={`/usuarios/${selected.participant.id}`} className="flex min-w-0 items-center gap-3">
                                    <img src={selected.participant.avatar_url} alt="" className="h-11 w-11 rounded-full object-cover" />
                                    <span className="min-w-0">
                                        <strong className="block truncate">{selected.participant.nome} {selected.participant.sobrenome}</strong>
                                        <span className="text-xs text-text-muted">{presenceLabel(selected.participant.online)}</span>
                                    </span>
                                </Link>
                                <Button type="button" variant="secondary" onClick={() => void refreshSelected()} disabled={messagesLoading}>Atualizar</Button>
                            </header>

                            <div className="flex-1 overflow-y-auto p-4 sm:p-6">
                                {hasMore && (
                                    <div className="mb-4 text-center">
                                        <Button type="button" variant="secondary" onClick={() => void loadOlder()} disabled={messagesLoading}>Carregar anteriores</Button>
                                    </div>
                                )}
                                {messagesLoading && messages.length === 0 ? (
                                    <p className="text-center text-sm text-text-muted">Carregando mensagens...</p>
                                ) : messages.length === 0 ? (
                                    <p className="text-center text-sm text-text-muted">Ainda não há mensagens. Comece a conversa.</p>
                                ) : (
                                    <ol className="space-y-3" aria-live="polite">
                                        {messages.map((message) => {
                                            const mine = message.sender_id === user?.id;
                                            return (
                                                <li key={message.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
                                                    <div className={`max-w-[85%] rounded-card border border-border px-4 py-3 sm:max-w-[70%] ${mine ? "bg-surface-muted" : "bg-surface"}`}>
                                                        <p className="whitespace-pre-wrap break-words text-sm text-text">{message.content}</p>
                                                        <time className="mt-1 block text-right text-[11px] text-text-muted" dateTime={message.created_at}>
                                                            {new Date(message.created_at).toLocaleString("pt-BR", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" })}
                                                        </time>
                                                    </div>
                                                </li>
                                            );
                                        })}
                                    </ol>
                                )}
                            </div>

                            <form onSubmit={sendMessage} className="border-t border-border p-4">
                                <label htmlFor="chat-message" className="sr-only">Mensagem</label>
                                <div className="flex items-end gap-2">
                                    <textarea
                                        id="chat-message"
                                        className="base-input min-h-12 flex-1 resize-y"
                                        value={draft}
                                        onChange={(event) => setDraft(event.target.value)}
                                        maxLength={2000}
                                        placeholder={selected.participant.active ? "Escreva uma mensagem..." : "Usuário indisponível"}
                                        disabled={sending || !selected.participant.active}
                                        rows={2}
                                    />
                                    <Button type="submit" loading={sending} disabled={!draft.trim() || !selected.participant.active}>Enviar</Button>
                                </div>
                                <p className="mt-1 text-right text-xs text-text-muted">{draft.length}/2000</p>
                            </form>
                        </>
                    )}
                </Card>
            </div>
        </section>
    );
}
