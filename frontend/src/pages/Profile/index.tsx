import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useUser } from "@/hooks/useUser";
import { apiConfig } from "@/services/api/apiConfig";

type PublicProfile = {
    id: number;
    nome: string;
    sobrenome: string;
    tipo_usuario: "aluno" | "instrutor" | "admin";
    data_cadastro: string;
    friend_code: string;
    avatar_url: string;
    online: boolean | null;
};
type OwnProfile = PublicProfile & { email: string; data_nascimento: string; ultimo_login: string | null; ultima_atualizacao: string; };
type FriendRequest = { id: number; direction: "incoming" | "outgoing"; requester_id: number; created_at: string; user: PublicProfile; };
type FriendRequests = { incoming: FriendRequest[]; outgoing: FriendRequest[]; };

const ROLE_LABEL: Record<PublicProfile["tipo_usuario"], string> = { aluno: "Aluno", instrutor: "Instrutor", admin: "Administrador" };

function messageFromError(error: unknown, fallback: string) {
    if (typeof error === "object" && error !== null && "response" in error) {
        const response = (error as { response?: { data?: { detail?: string; message?: string } } }).response;
        return response?.data?.detail || response?.data?.message || fallback;
    }
    return fallback;
}

function presenceLabel(value: boolean | null) {
    if (value === null) return "Presença privada";
    return value ? "● Online" : "○ Offline";
}

export default function Profile() {
    const { userId } = useParams();
    const { user, refreshUser } = useUser();
    const ownProfile = !userId;
    const targetId = userId ? Number(userId) : user?.id;
    const [profile, setProfile] = useState<OwnProfile | PublicProfile | null>(null);
    const [friends, setFriends] = useState<PublicProfile[]>([]);
    const [requests, setRequests] = useState<FriendRequests>({ incoming: [], outgoing: [] });
    const [search, setSearch] = useState("");
    const [searchResults, setSearchResults] = useState<PublicProfile[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [avatarBusy, setAvatarBusy] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [notice, setNotice] = useState<string | null>(null);
    const [avatarVersion, setAvatarVersion] = useState(0);
    const friendIds = useMemo(() => new Set(friends.map((friend) => friend.id)), [friends]);
    const incomingIds = useMemo(() => new Set(requests.incoming.map((request) => request.user.id)), [requests.incoming]);
    const outgoingIds = useMemo(() => new Set(requests.outgoing.map((request) => request.user.id)), [requests.outgoing]);

    async function loadSocial() {
        const [friendsResponse, requestsResponse] = await Promise.all([
            apiConfig().get("/users/friends"),
            apiConfig().get("/users/friend-requests"),
        ]);
        setFriends(friendsResponse.data.data ?? []);
        setRequests(requestsResponse.data.data ?? { incoming: [], outgoing: [] });
    }

    async function reloadTarget() {
        if (!targetId) return;
        const response = await apiConfig().get(ownProfile ? "/users/me" : `/users/${targetId}`);
        setProfile(response.data.data);
    }

    useEffect(() => {
        if (!targetId) return;
        let active = true;
        setLoading(true);
        Promise.all([
            apiConfig().get(ownProfile ? "/users/me" : `/users/${targetId}`),
            apiConfig().get("/users/friends"),
            apiConfig().get("/users/friend-requests"),
        ]).then(([profileResponse, friendsResponse, requestsResponse]) => {
            if (!active) return;
            setProfile(profileResponse.data.data);
            setFriends(friendsResponse.data.data ?? []);
            setRequests(requestsResponse.data.data ?? { incoming: [], outgoing: [] });
            setError(null);
        }).catch((err) => active && setError(messageFromError(err, "Não foi possível carregar o perfil.")))
          .finally(() => active && setLoading(false));
        return () => { active = false; };
    }, [targetId, ownProfile]);

    useEffect(() => {
        if (!user) return;
        const heartbeat = () => { void apiConfig().post("/users/presence/heartbeat").catch(() => undefined); };
        heartbeat();
        const timer = window.setInterval(heartbeat, 30000);
        return () => window.clearInterval(timer);
    }, [user]);

    async function saveProfile(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        if (!ownProfile || !profile || !("email" in profile)) return;
        const form = new FormData(event.currentTarget);
        setSaving(true); setError(null); setNotice(null);
        try {
            const response = await apiConfig().patch("/users/me", {
                nome: String(form.get("nome") ?? "").trim(), sobrenome: String(form.get("sobrenome") ?? "").trim(),
                email: String(form.get("email") ?? "").trim(), data_nascimento: String(form.get("data_nascimento") ?? ""),
            });
            setProfile(response.data.data); await refreshUser(); setNotice("Perfil atualizado e persistido.");
        } catch (err) { setError(messageFromError(err, "Não foi possível atualizar o perfil.")); }
        finally { setSaving(false); }
    }

    async function uploadAvatar(file: File | null) {
        if (!file) return;
        if (!["image/png", "image/jpeg", "image/webp"].includes(file.type)) { setError("Avatar deve ser PNG, JPEG ou WebP."); return; }
        if (file.size === 0 || file.size > 8 * 1024 * 1024) { setError("Avatar deve ter entre 1 byte e 8 MB."); return; }
        setAvatarBusy(true); setProgress(0); setError(null); setNotice(null);
        try {
            const form = new FormData(); form.append("file", file, file.name); form.append("purpose", "avatar");
            const uploaded = await apiConfig().post("/files", form, { onUploadProgress: (event) => { if (event.total) setProgress(Math.round(event.loaded * 100 / event.total)); } });
            const response = await apiConfig().put(`/users/me/avatar/${uploaded.data.data.id}`);
            setProfile(response.data.data); setAvatarVersion((value) => value + 1); setNotice("Avatar atualizado.");
        } catch (err) { setError(messageFromError(err, "Não foi possível atualizar o avatar.")); }
        finally { setAvatarBusy(false); }
    }

    async function removeAvatar() {
        setAvatarBusy(true); setError(null);
        try { const response = await apiConfig().delete("/users/me/avatar"); setProfile(response.data.data); setAvatarVersion((v) => v + 1); setNotice("Avatar padrão restaurado."); }
        catch (err) { setError(messageFromError(err, "Não foi possível remover o avatar.")); }
        finally { setAvatarBusy(false); }
    }

    async function searchUsers(event: FormEvent<HTMLFormElement>) {
        event.preventDefault(); setError(null);
        try { const response = await apiConfig().get("/users", { params: { q: search, limit: 20 } }); setSearchResults(response.data.data ?? []); }
        catch (err) { setError(messageFromError(err, "Não foi possível buscar usuários.")); }
    }

    async function sendFriendRequest(id: number) {
        try {
            await apiConfig().post(`/users/friend-requests/${id}`);
            await loadSocial();
            setNotice("Solicitação de amizade enviada."); setError(null);
        } catch (err) { setError(messageFromError(err, "Não foi possível enviar a solicitação.")); }
    }

    async function acceptFriendRequest(id: number) {
        try {
            await apiConfig().post(`/users/friend-requests/${id}/accept`);
            await loadSocial(); await reloadTarget();
            setNotice("Solicitação aceita."); setError(null);
        } catch (err) { setError(messageFromError(err, "Não foi possível aceitar a solicitação.")); }
    }

    async function removeFriendRequest(id: number) {
        try {
            await apiConfig().delete(`/users/friend-requests/${id}`);
            await loadSocial();
            setNotice("Solicitação removida."); setError(null);
        } catch (err) { setError(messageFromError(err, "Não foi possível remover a solicitação.")); }
    }

    async function removeFriend(id: number) {
        try {
            await apiConfig().delete(`/users/friends/${id}`);
            await loadSocial(); await reloadTarget();
            setNotice("Amigo removido."); setError(null);
        } catch (err) { setError(messageFromError(err, "Não foi possível remover o amigo.")); }
    }

    function socialAction(target: PublicProfile) {
        if (friendIds.has(target.id)) return <Button type="button" variant="secondary" onClick={() => void removeFriend(target.id)}>Remover amigo</Button>;
        if (incomingIds.has(target.id)) return <><Button type="button" onClick={() => void acceptFriendRequest(target.id)}>Aceitar</Button><Button type="button" variant="secondary" onClick={() => void removeFriendRequest(target.id)}>Recusar</Button></>;
        if (outgoingIds.has(target.id)) return <Button type="button" variant="secondary" onClick={() => void removeFriendRequest(target.id)}>Cancelar solicitação</Button>;
        return <Button type="button" variant="secondary" onClick={() => void sendFriendRequest(target.id)}>Adicionar amigo</Button>;
    }

    if (loading) return <section className="mx-auto max-w-5xl px-4 py-10 text-text-muted">Carregando perfil...</section>;
    if (!profile) return <section className="mx-auto max-w-5xl px-4 py-10 text-danger">{error ?? "Perfil não encontrado."}</section>;
    const avatarSrc = `${profile.avatar_url}${profile.avatar_url.includes("?") ? "&" : "?"}v=${avatarVersion}`;

    return <section className="mx-auto w-full max-w-5xl px-4 py-10 md:px-8">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center">
            <img src={avatarSrc} alt={`Avatar de ${profile.nome}`} className="h-28 w-28 rounded-full border border-border object-cover" />
            <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-primary">{ROLE_LABEL[profile.tipo_usuario]}</p>
                <h1 className="text-3xl font-bold text-text">{profile.nome} {profile.sobrenome}</h1>
                <p className="mt-1 text-sm text-text-muted">{presenceLabel(profile.online)}</p>
                <p className="mt-1 text-sm text-text-muted">Friend Code: <code className="font-semibold text-text">{profile.friend_code}</code></p>
            </div>
        </div>
        {error && <p role="alert" className="mb-4 rounded-card border border-danger p-3 text-danger">{error}</p>}
        {notice && <p role="status" className="mb-4 rounded-card border border-success p-3 text-text">{notice}</p>}

        {ownProfile && "email" in profile ? <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <Card className="p-6"><h2 className="mb-4 text-xl font-semibold">Editar perfil</h2><form className="space-y-4" onSubmit={saveProfile}>
                <label className="block"><span className="mb-1 block text-sm font-medium">Nome</span><input className="base-input w-full" name="nome" defaultValue={profile.nome} required maxLength={45} /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium">Sobrenome</span><input className="base-input w-full" name="sobrenome" defaultValue={profile.sobrenome} required maxLength={45} /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium">Email</span><input className="base-input w-full" name="email" type="email" defaultValue={profile.email} required /></label>
                <label className="block"><span className="mb-1 block text-sm font-medium">Data de nascimento</span><input className="base-input w-full" name="data_nascimento" type="date" defaultValue={profile.data_nascimento} required /></label>
                <Button type="submit" loading={saving}>Salvar alterações</Button>
            </form></Card>
            <Card className="p-6"><h2 className="mb-4 text-xl font-semibold">Avatar</h2><label htmlFor="profile-avatar" className="block text-sm font-medium">PNG, JPEG ou WebP, até 8 MB</label><input id="profile-avatar" type="file" accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp" disabled={avatarBusy} onChange={(event) => void uploadAvatar(event.target.files?.[0] ?? null)} className="base-input mt-2 w-full" />{avatarBusy && <progress className="mt-4 w-full" max={100} value={progress} />}<Button type="button" variant="secondary" className="mt-4" onClick={removeAvatar} disabled={avatarBusy}>Usar avatar padrão</Button></Card>
        </div> : <Card className="p-6"><p className="text-text-muted">Membro desde {new Date(profile.data_cadastro).toLocaleDateString("pt-BR")}.</p><div className="mt-4 flex flex-wrap gap-2"><Link to={`/chat?user=${profile.id}`}><Button type="button">Conversar</Button></Link>{socialAction(profile)}</div></Card>}

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <Card className="p-6"><h2 className="mb-4 text-xl font-semibold">Amigos</h2>{friends.length === 0 ? <p className="text-text-muted">Nenhum amigo adicionado ainda.</p> : <ul className="space-y-3">{friends.map((friend) => <li key={friend.id} className="flex flex-wrap items-center justify-between gap-3 rounded-card border border-border p-3"><Link className="flex min-w-0 items-center gap-3" to={`/usuarios/${friend.id}`}><img src={friend.avatar_url} alt="" className="h-10 w-10 rounded-full object-cover" /><span><strong className="block">{friend.nome} {friend.sobrenome}</strong><span className="text-sm text-text-muted">{presenceLabel(friend.online)}</span></span></Link><div className="flex gap-2"><Link to={`/chat?user=${friend.id}`}><Button type="button" variant="secondary">Chat</Button></Link><Button type="button" variant="secondary" onClick={() => void removeFriend(friend.id)}>Remover</Button></div></li>)}</ul>}</Card>

            {ownProfile && <Card className="p-6"><h2 className="mb-4 text-xl font-semibold">Encontrar usuários</h2><form className="flex gap-2" onSubmit={searchUsers}><input className="base-input min-w-0 flex-1" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Nome ou Friend Code" aria-label="Buscar usuários" /><Button type="submit">Buscar</Button></form><ul className="mt-4 space-y-3">{searchResults.map((result) => <li key={result.id} className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-3"><Link to={`/usuarios/${result.id}`}><span className="block">{result.nome} {result.sobrenome}</span><code className="text-xs text-text-muted">{result.friend_code}</code></Link><div className="flex flex-wrap gap-2">{friendIds.has(result.id) ? <span className="text-sm text-text-muted">Já é amigo</span> : incomingIds.has(result.id) ? <><Button type="button" onClick={() => void acceptFriendRequest(result.id)}>Aceitar</Button><Button type="button" variant="secondary" onClick={() => void removeFriendRequest(result.id)}>Recusar</Button></> : outgoingIds.has(result.id) ? <Button type="button" variant="secondary" onClick={() => void removeFriendRequest(result.id)}>Cancelar</Button> : <Button type="button" variant="secondary" onClick={() => void sendFriendRequest(result.id)}>Adicionar</Button>}</div></li>)}</ul></Card>}
        </div>

        {ownProfile && <Card className="mt-6 p-6">
            <h2 className="mb-4 text-xl font-semibold">Solicitações de amizade</h2>
            {requests.incoming.length === 0 && requests.outgoing.length === 0 ? <p className="text-text-muted">Nenhuma solicitação pendente.</p> : <div className="grid gap-6 md:grid-cols-2">
                <div><h3 className="mb-3 font-semibold">Recebidas</h3>{requests.incoming.length === 0 ? <p className="text-sm text-text-muted">Nenhuma solicitação recebida.</p> : <ul className="space-y-3">{requests.incoming.map((request) => <li key={request.id} className="rounded-card border border-border p-3"><Link to={`/usuarios/${request.user.id}`} className="font-medium">{request.user.nome} {request.user.sobrenome}</Link><code className="mt-1 block text-xs text-text-muted">{request.user.friend_code}</code><div className="mt-3 flex gap-2"><Button type="button" onClick={() => void acceptFriendRequest(request.user.id)}>Aceitar</Button><Button type="button" variant="secondary" onClick={() => void removeFriendRequest(request.user.id)}>Recusar</Button></div></li>)}</ul>}</div>
                <div><h3 className="mb-3 font-semibold">Enviadas</h3>{requests.outgoing.length === 0 ? <p className="text-sm text-text-muted">Nenhuma solicitação enviada.</p> : <ul className="space-y-3">{requests.outgoing.map((request) => <li key={request.id} className="rounded-card border border-border p-3"><Link to={`/usuarios/${request.user.id}`} className="font-medium">{request.user.nome} {request.user.sobrenome}</Link><code className="mt-1 block text-xs text-text-muted">{request.user.friend_code}</code><Button type="button" variant="secondary" className="mt-3" onClick={() => void removeFriendRequest(request.user.id)}>Cancelar</Button></li>)}</ul>}</div>
            </div>}
        </Card>}
    </section>;
}
