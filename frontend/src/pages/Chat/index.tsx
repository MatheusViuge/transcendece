import { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
    online: boolean;
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
    next_after_id?: number | null;
};

type ConversationCache = {
    messages: ChatMessage[];
    hasMore: boolean;
    nextBeforeId: number | null;
    loaded: boolean;
    loading: boolean;
};

type RealtimeStatus = "connecting" | "online" | "reconnecting" | "offline";

const EMPTY_CACHE: ConversationCache = {
    messages: [],
    hasMore: false,
    nextBeforeId: null,
    loaded: false,
    loading: false,
};

function messageFromError(error: unknown, fallback: string) {
    if (typeof error === "object" && error !== null && "response" in error) {
        const response = (error as { response?: { data?: { detail?: string; message?: string } } }).response;
        return response?.data?.detail || response?.data?.message || fallback;
    }
    return fallback;
}

function mergeMessages(current: ChatMessage[], incoming: ChatMessage[]): ChatMessage[] {
    const byId = new Map<number, ChatMessage>();
    for (const message of [...current, ...incoming]) byId.set(message.id, message);
    return [...byId.values()].sort((left, right) => left.id - right.id);
}

function realtimeUrl(): string {
    const apiBase = new URL(import.meta.env.VITE_API_URL || "/api", window.location.origin);
    apiBase.protocol = apiBase.protocol === "https:" ? "wss:" : "ws:";
    apiBase.pathname = `${apiBase.pathname.replace(/\/$/, "")}/ws/chat`;
    apiBase.search = "";
    apiBase.hash = "";
    return apiBase.toString();
}

function realtimeLabel(status: RealtimeStatus): string {
    if (status === "online") return "Tempo real conectado";
    if (status === "reconnecting") return "Reconectando tempo real";
    if (status === "connecting") return "Conectando tempo real";
    return "Tempo real offline";
}

export default function Chat() {
    const { user } = useUser();
    const [searchParams, setSearchParams] = useSearchParams();
    const recipientId = Number(searchParams.get("user") ?? 0);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [selectedId, setSelectedId] = useState<number | null>(null);
    const [messageCache, setMessageCache] = useState<Record<number, ConversationCache>>({});
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [draft, setDraft] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [realtimeStatus, setRealtimeStatus] = useState<RealtimeStatus>("offline");

    const cacheRef = useRef(messageCache);
    const selectedIdRef = useRef(selectedId);
    const scrollRef = useRef<HTMLDivElement | null>(null);
    const topSentinelRef = useRef<HTMLDivElement | null>(null);
    const socketRef = useRef<WebSocket | null>(null);
    const nearBottomRef = useRef(true);
    const userGenerationRef = useRef(0);

    useEffect(() => {
        cacheRef.current = messageCache;
    }, [messageCache]);

    useEffect(() => {
        selectedIdRef.current = selectedId;
    }, [selectedId]);

    const selected = useMemo(
        () => conversations.find((conversation) => conversation.id === selectedId) ?? null,
        [conversations, selectedId],
    );
    const selectedCache = selectedId ? messageCache[selectedId] : undefined;
    const messages = selectedCache?.messages ?? [];
    const messagesLoading = selectedCache?.loading ?? false;
    const hasMore = selectedCache?.hasMore ?? false;

    const fetchConversations = useCallback(async (preferredId?: number) => {
        const response = await apiConfig().get("/chat/conversations", { params: { limit: 100 } });
        const items: Conversation[] = response.data.data.items ?? [];
        setConversations(items);
        setSelectedId((current) => {
            if (preferredId && items.some((item) => item.id === preferredId)) return preferredId;
            if (current && items.some((item) => item.id === current)) return current;
            return items[0]?.id ?? null;
        });
        return items;
    }, []);

    useEffect(() => {
        userGenerationRef.current += 1;
        cacheRef.current = {};
        setMessageCache({});
        setConversations([]);
        setSelectedId(null);
        nearBottomRef.current = true;
    }, [user?.id]);

    useEffect(() => {
        let active = true;
        const generation = userGenerationRef.current;
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
                if (!active || generation !== userGenerationRef.current) return;
                await fetchConversations(preferredId);
            } catch (err) {
                if (active && generation === userGenerationRef.current) {
                    setError(messageFromError(err, "Não foi possível carregar suas conversas."));
                }
            } finally {
                if (active && generation === userGenerationRef.current) setLoading(false);
            }
        };
        void initialize();
        return () => { active = false; };
    }, [fetchConversations, recipientId, setSearchParams, user?.id]);

    const ensureConversationLoaded = useCallback(async (conversationId: number) => {
        const existing = cacheRef.current[conversationId];
        if (existing?.loaded || existing?.loading) return;
        const generation = userGenerationRef.current;
        setMessageCache((current) => ({
            ...current,
            [conversationId]: { ...(current[conversationId] ?? EMPTY_CACHE), loading: true },
        }));
        try {
            const response = await apiConfig().get(`/chat/conversations/${conversationId}/messages`, {
                params: { limit: 30 },
            });
            if (generation !== userGenerationRef.current) return;
            const page: MessagePage = response.data.data;
            setMessageCache((current) => ({
                ...current,
                [conversationId]: {
                    messages: page.items ?? [],
                    hasMore: page.has_more,
                    nextBeforeId: page.next_before_id,
                    loaded: true,
                    loading: false,
                },
            }));
            if (selectedIdRef.current === conversationId) {
                nearBottomRef.current = true;
                window.requestAnimationFrame(() => {
                    const element = scrollRef.current;
                    if (element) element.scrollTop = element.scrollHeight;
                });
            }
        } catch (err) {
            if (generation !== userGenerationRef.current) return;
            setMessageCache((current) => ({
                ...current,
                [conversationId]: { ...(current[conversationId] ?? EMPTY_CACHE), loading: false },
            }));
            setError(messageFromError(err, "Não foi possível carregar o histórico."));
        }
    }, []);

    useEffect(() => {
        if (!selectedId) return;
        nearBottomRef.current = true;
        const existing = cacheRef.current[selectedId];
        if (existing?.loaded) {
            window.requestAnimationFrame(() => {
                const element = scrollRef.current;
                if (element) element.scrollTop = element.scrollHeight;
            });
            return;
        }
        void ensureConversationLoaded(selectedId);
    }, [ensureConversationLoaded, selectedId]);

    const appendMessage = useCallback((message: ChatMessage) => {
        setMessageCache((current) => {
            const entry = current[message.conversation_id] ?? {
                ...EMPTY_CACHE,
                loaded: true,
            };
            return {
                ...current,
                [message.conversation_id]: {
                    ...entry,
                    messages: mergeMessages(entry.messages, [message]),
                },
            };
        });

        setConversations((current) => {
            const exists = current.some((conversation) => conversation.id === message.conversation_id);
            if (!exists) {
                void fetchConversations(message.conversation_id);
                return current;
            }
            return current
                .map((conversation) => conversation.id === message.conversation_id
                    ? { ...conversation, last_message: message, updated_at: message.created_at }
                    : conversation)
                .sort((left, right) => new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime());
        });

        if (selectedIdRef.current === message.conversation_id && nearBottomRef.current) {
            window.requestAnimationFrame(() => {
                const element = scrollRef.current;
                if (element) element.scrollTop = element.scrollHeight;
            });
        }
    }, [fetchConversations]);

    const recoverGaps = useCallback(async () => {
        const generation = userGenerationRef.current;
        for (const [conversationKey, entry] of Object.entries(cacheRef.current)) {
            if (!entry.loaded || entry.messages.length === 0) continue;
            const conversationId = Number(conversationKey);
            let afterId = entry.messages[entry.messages.length - 1].id;
            let keepLoading = true;
            while (keepLoading) {
                const response = await apiConfig().get(`/chat/conversations/${conversationId}/messages`, {
                    params: { limit: 100, after_id: afterId },
                });
                if (generation !== userGenerationRef.current) return;
                const page: MessagePage = response.data.data;
                const incoming = page.items ?? [];
                if (incoming.length > 0) {
                    setMessageCache((current) => {
                        const currentEntry = current[conversationId] ?? entry;
                        return {
                            ...current,
                            [conversationId]: {
                                ...currentEntry,
                                messages: mergeMessages(currentEntry.messages, incoming),
                            },
                        };
                    });
                    afterId = incoming[incoming.length - 1].id;
                }
                keepLoading = Boolean(page.has_more && page.next_after_id && incoming.length > 0);
                if (page.next_after_id) afterId = page.next_after_id;
            }
        }
        if (generation === userGenerationRef.current) {
            await fetchConversations(selectedIdRef.current ?? undefined);
        }
    }, [fetchConversations]);

    useEffect(() => {
        if (!user?.id) {
            setRealtimeStatus("offline");
            return;
        }

        let stopped = false;
        let reconnectTimer: number | null = null;
        let pingTimer: number | null = null;
        let attempt = 0;

        const clearPing = () => {
            if (pingTimer !== null) window.clearInterval(pingTimer);
            pingTimer = null;
        };

        const connect = () => {
            if (stopped) return;
            const token = localStorage.getItem("token");
            if (!token) {
                setRealtimeStatus("offline");
                return;
            }

            setRealtimeStatus(attempt > 0 ? "reconnecting" : "connecting");
            const socket = new WebSocket(realtimeUrl());
            socketRef.current = socket;

            socket.onopen = () => {
                socket.send(JSON.stringify({ type: "auth", token }));
            };

            socket.onmessage = (event) => {
                let payload: unknown;
                try {
                    payload = JSON.parse(event.data as string);
                } catch {
                    return;
                }
                if (typeof payload !== "object" || payload === null || !("event" in payload)) return;
                const realtimeEvent = payload as { event: string } & Partial<ChatMessage>;
                if (realtimeEvent.event === "realtime.ready") {
                    attempt = 0;
                    setRealtimeStatus("online");
                    clearPing();
                    pingTimer = window.setInterval(() => {
                        if (socket.readyState === WebSocket.OPEN) {
                            socket.send(JSON.stringify({ type: "ping" }));
                        }
                    }, 25_000);
                    void recoverGaps().catch(() => {
                        setError("Reconectado, mas não foi possível sincronizar mensagens perdidas.");
                    });
                    return;
                }
                if (realtimeEvent.event === "chat.message.created") {
                    const message = realtimeEvent as ChatMessage;
                    if (typeof message.id === "number" && typeof message.conversation_id === "number") {
                        appendMessage(message);
                    }
                }
            };

            socket.onerror = () => {
                socket.close();
            };

            socket.onclose = () => {
                clearPing();
                if (socketRef.current === socket) socketRef.current = null;
                if (stopped) return;
                setRealtimeStatus("reconnecting");
                const delay = Math.min(10_000, 1_000 * 2 ** attempt);
                attempt += 1;
                reconnectTimer = window.setTimeout(connect, delay);
            };
        };

        connect();
        return () => {
            stopped = true;
            clearPing();
            if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
            const socket = socketRef.current;
            socketRef.current = null;
            if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
                socket.close(1000, "session ended");
            }
            setRealtimeStatus("offline");
        };
    }, [appendMessage, recoverGaps, user?.id]);

    const loadOlder = useCallback(async () => {
        if (!selectedId) return;
        const entry = cacheRef.current[selectedId];
        if (!entry?.hasMore || !entry.nextBeforeId || entry.loading) return;
        const generation = userGenerationRef.current;
        const scrollElement = scrollRef.current;
        const previousHeight = scrollElement?.scrollHeight ?? 0;
        const previousTop = scrollElement?.scrollTop ?? 0;

        setMessageCache((current) => ({
            ...current,
            [selectedId]: { ...(current[selectedId] ?? entry), loading: true },
        }));
        try {
            const response = await apiConfig().get(`/chat/conversations/${selectedId}/messages`, {
                params: { limit: 30, before_id: entry.nextBeforeId },
            });
            if (generation !== userGenerationRef.current) return;
            const page: MessagePage = response.data.data;
            setMessageCache((current) => {
                const currentEntry = current[selectedId] ?? entry;
                return {
                    ...current,
                    [selectedId]: {
                        ...currentEntry,
                        messages: mergeMessages(page.items ?? [], currentEntry.messages),
                        hasMore: page.has_more,
                        nextBeforeId: page.next_before_id,
                        loaded: true,
                        loading: false,
                    },
                };
            });
            window.requestAnimationFrame(() => {
                const element = scrollRef.current;
                if (element) element.scrollTop = element.scrollHeight - previousHeight + previousTop;
            });
        } catch (err) {
            if (generation !== userGenerationRef.current) return;
            setMessageCache((current) => ({
                ...current,
                [selectedId]: { ...(current[selectedId] ?? entry), loading: false },
            }));
            setError(messageFromError(err, "Não foi possível carregar mensagens anteriores."));
        }
    }, [selectedId]);

    useEffect(() => {
        const sentinel = topSentinelRef.current;
        const root = scrollRef.current;
        if (!sentinel || !root || !selectedId || !hasMore) return;
        const observer = new IntersectionObserver((entries) => {
            if (entries.some((entry) => entry.isIntersecting)) void loadOlder();
        }, { root, rootMargin: "120px 0px 0px", threshold: 0.01 });
        observer.observe(sentinel);
        return () => observer.disconnect();
    }, [hasMore, loadOlder, selectedId]);

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
            appendMessage(response.data.data as ChatMessage);
            setDraft("");
        } catch (err) {
            setError(messageFromError(err, "Não foi possível enviar a mensagem. Tente novamente."));
        } finally {
            setSending(false);
        }
    }

    function handleScroll() {
        const element = scrollRef.current;
        if (!element) return;
        nearBottomRef.current = element.scrollHeight - element.scrollTop - element.clientHeight < 96;
    }

    if (loading) return <section className="mx-auto max-w-6xl px-4 py-10 text-text-muted">Carregando conversas...</section>;

    return (
        <section className="mx-auto w-full max-w-6xl px-4 py-8 md:px-8">
            <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
                <div>
                    <p className="text-sm font-semibold uppercase tracking-wide text-primary">Interações</p>
                    <h1 className="text-3xl font-bold text-text">Chat</h1>
                    <p className="mt-1 text-sm text-text-muted">Mensagens persistentes com atualização imediata por WebSocket.</p>
                </div>
                <span
                    className="rounded-pill border border-border bg-surface px-3 py-1 text-xs text-text-muted"
                    role="status"
                    aria-live="polite"
                >
                    {realtimeLabel(realtimeStatus)}
                </span>
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
                                            <span className="text-xs text-text-muted" aria-label={conversation.participant.online ? "Online" : "Offline"}>
                                                {conversation.participant.online ? "●" : "○"}
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
                                        <span className="text-xs text-text-muted">{selected.participant.online ? "Online" : "Offline"}</span>
                                    </span>
                                </Link>
                                <span className="text-xs text-text-muted">{realtimeStatus === "online" ? "● realtime" : "○ conectando"}</span>
                            </header>

                            <div ref={scrollRef} onScroll={handleScroll} className="flex-1 overflow-y-auto p-4 sm:p-6">
                                <div ref={topSentinelRef} aria-hidden="true" className="h-px" />
                                {hasMore && (
                                    <div className="mb-4 text-center">
                                        <Button type="button" variant="secondary" onClick={() => void loadOlder()} disabled={messagesLoading}>
                                            {messagesLoading ? "Carregando..." : "Carregar anteriores"}
                                        </Button>
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
