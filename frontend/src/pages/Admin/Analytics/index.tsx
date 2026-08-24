import { useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { useUser } from "@/hooks/useUser";
import { apiConfig } from "@/services/api/apiConfig";

type Kpis = {
    new_users: number;
    courses_created: number;
    enrollments: number;
    completion_rate: number;
    average_rating: number;
    chat_messages: number;
};

type DailyPoint = { date: string; registrations: number; enrollments: number };
type BarPoint = { course_id: number; label: string; value: number };
type PiePoint = { label: string; value: number };
type CategoryOption = { id: number; name: string };

type DashboardSnapshot = {
    generated_at: string;
    filters: {
        start_date: string;
        end_date: string;
        category_id: number | null;
        enrollment_status: string | null;
    };
    filter_options: {
        categories: CategoryOption[];
        enrollment_statuses: string[];
    };
    kpis: Kpis;
    daily_activity: DailyPoint[];
    top_courses: BarPoint[];
    enrollment_statuses: PiePoint[];
};

type RealtimeStatus = "connecting" | "online" | "reconnecting" | "offline";

function isoDate(value: Date) {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, "0");
    const day = String(value.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function initialDates() {
    const end = new Date();
    const start = new Date(end);
    start.setDate(start.getDate() - 29);
    return { start: isoDate(start), end: isoDate(end) };
}

function analyticsWsUrl(): string {
    const apiBase = new URL(import.meta.env.VITE_API_URL || "/api", window.location.origin);
    apiBase.protocol = apiBase.protocol === "https:" ? "wss:" : "ws:";
    apiBase.pathname = `${apiBase.pathname.replace(/\/$/, "")}/ws/analytics`;
    apiBase.search = "";
    apiBase.hash = "";
    return apiBase.toString();
}

function formatNumber(value: number) {
    return new Intl.NumberFormat("pt-BR").format(value);
}

function formatPercent(value: number) {
    return `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(value)}%`;
}

function LineChart({ data }: { data: DailyPoint[] }) {
    const [active, setActive] = useState<string | null>(null);
    const width = 720;
    const height = 250;
    const padding = 28;
    const maxValue = Math.max(1, ...data.flatMap((item) => [item.registrations, item.enrollments]));
    const xFor = (index: number) => data.length <= 1
        ? width / 2
        : padding + (index / (data.length - 1)) * (width - padding * 2);
    const yFor = (value: number) => height - padding - (value / maxValue) * (height - padding * 2);
    const registrationPoints = data.map((item, index) => `${xFor(index)},${yFor(item.registrations)}`).join(" ");
    const enrollmentPoints = data.map((item, index) => `${xFor(index)},${yFor(item.enrollments)}`).join(" ");

    if (data.length === 0) return <p className="text-sm text-text-muted">Sem atividade no período.</p>;

    return (
        <div>
            <div className="mb-2 flex flex-wrap gap-4 text-xs text-text-muted">
                <span>● Cadastros</span><span>○ Matrículas</span>
            </div>
            <svg viewBox={`0 0 ${width} ${height}`} className="h-64 w-full" role="img" aria-label="Atividade diária de cadastros e matrículas">
                <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="var(--color-border)" />
                <polyline fill="none" stroke="var(--color-primary)" strokeWidth="3" points={registrationPoints} />
                <polyline fill="none" stroke="var(--color-success)" strokeWidth="3" strokeDasharray="7 4" points={enrollmentPoints} />
                {data.map((item, index) => (
                    <g key={item.date}>
                        <circle
                            cx={xFor(index)} cy={yFor(item.registrations)} r="5"
                            fill="var(--color-primary)" tabIndex={0}
                            onMouseEnter={() => setActive(`${item.date}: ${item.registrations} cadastro(s)`)}
                            onFocus={() => setActive(`${item.date}: ${item.registrations} cadastro(s)`)}
                            onMouseLeave={() => setActive(null)} onBlur={() => setActive(null)}
                        />
                        <circle
                            cx={xFor(index)} cy={yFor(item.enrollments)} r="5"
                            fill="var(--color-success)" tabIndex={0}
                            onMouseEnter={() => setActive(`${item.date}: ${item.enrollments} matrícula(s)`)}
                            onFocus={() => setActive(`${item.date}: ${item.enrollments} matrícula(s)`)}
                            onMouseLeave={() => setActive(null)} onBlur={() => setActive(null)}
                        />
                    </g>
                ))}
            </svg>
            <p className="min-h-5 text-center text-xs text-text-muted" aria-live="polite">{active ?? "Passe o mouse ou use Tab nos pontos para inspecionar valores."}</p>
        </div>
    );
}

function BarChart({ data }: { data: BarPoint[] }) {
    const [active, setActive] = useState<string | null>(null);
    const maxValue = Math.max(1, ...data.map((item) => item.value));
    if (data.length === 0) return <p className="text-sm text-text-muted">Sem matrículas para ranquear cursos neste recorte.</p>;
    return (
        <div className="space-y-3">
            {data.map((item) => (
                <button
                    type="button" key={item.course_id}
                    className="block w-full rounded-control text-left focus-visible:outline-primary"
                    onMouseEnter={() => setActive(`${item.label}: ${item.value} matrícula(s)`)}
                    onFocus={() => setActive(`${item.label}: ${item.value} matrícula(s)`)}
                    onMouseLeave={() => setActive(null)} onBlur={() => setActive(null)}
                >
                    <span className="mb-1 flex justify-between gap-3 text-xs text-text-muted">
                        <span className="truncate">{item.label}</span><strong>{item.value}</strong>
                    </span>
                    <span className="block h-3 overflow-hidden rounded-pill bg-surface-muted">
                        <span className="block h-full rounded-pill bg-primary" style={{ width: `${(item.value / maxValue) * 100}%` }} />
                    </span>
                </button>
            ))}
            <p className="min-h-5 text-xs text-text-muted" aria-live="polite">{active ?? "Foque uma barra para ver o valor exato."}</p>
        </div>
    );
}

const PIE_COLORS = ["var(--color-primary)", "var(--color-success)", "var(--color-warning)", "var(--color-danger)"];

function PieChart({ data }: { data: PiePoint[] }) {
    const [active, setActive] = useState<string | null>(null);
    const total = data.reduce((sum, item) => sum + item.value, 0);
    const gradient = useMemo(() => {
        if (!total) return "var(--color-surface-muted)";
        let cursor = 0;
        const parts = data.map((item, index) => {
            const start = cursor;
            const end = cursor + (item.value / total) * 100;
            cursor = end;
            return `${PIE_COLORS[index % PIE_COLORS.length]} ${start}% ${end}%`;
        });
        return `conic-gradient(${parts.join(", ")})`;
    }, [data, total]);

    if (!total) return <p className="text-sm text-text-muted">Sem distribuição de status no período.</p>;
    return (
        <div className="grid items-center gap-5 sm:grid-cols-[180px_1fr]">
            <div className="mx-auto aspect-square w-40 rounded-full border border-border" style={{ background: gradient }} role="img" aria-label="Distribuição de status das matrículas" />
            <div className="space-y-2">
                {data.map((item, index) => {
                    const percent = (item.value / total) * 100;
                    return (
                        <button
                            key={item.label} type="button"
                            className="flex w-full items-center justify-between gap-3 rounded-control px-2 py-1 text-sm hover:bg-surface-muted"
                            onMouseEnter={() => setActive(`${item.label}: ${item.value} (${formatPercent(percent)})`)}
                            onFocus={() => setActive(`${item.label}: ${item.value} (${formatPercent(percent)})`)}
                            onMouseLeave={() => setActive(null)} onBlur={() => setActive(null)}
                        >
                            <span className="flex items-center gap-2">
                                <span className="h-3 w-3 rounded-full" style={{ background: PIE_COLORS[index % PIE_COLORS.length] }} />
                                <span className="capitalize">{item.label}</span>
                            </span>
                            <strong>{formatPercent(percent)}</strong>
                        </button>
                    );
                })}
                <p className="min-h-5 text-xs text-text-muted" aria-live="polite">{active ?? "Foque uma fatia pela legenda para inspecionar."}</p>
            </div>
        </div>
    );
}

export default function AdminAnalytics() {
    const { user } = useUser();
    const defaults = useMemo(initialDates, []);
    const [startDate, setStartDate] = useState(defaults.start);
    const [endDate, setEndDate] = useState(defaults.end);
    const [categoryId, setCategoryId] = useState("");
    const [enrollmentStatus, setEnrollmentStatus] = useState("");
    const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [realtimeStatus, setRealtimeStatus] = useState<RealtimeStatus>("offline");
    const [exporting, setExporting] = useState<"csv" | "pdf" | null>(null);
    const socketRef = useRef<WebSocket | null>(null);
    const filtersRef = useRef({ startDate, endDate, categoryId, enrollmentStatus });

    const params = useMemo(() => ({
        start_date: startDate,
        end_date: endDate,
        ...(categoryId ? { category_id: Number(categoryId) } : {}),
        ...(enrollmentStatus ? { enrollment_status: enrollmentStatus } : {}),
    }), [categoryId, endDate, enrollmentStatus, startDate]);

    useEffect(() => {
        filtersRef.current = { startDate, endDate, categoryId, enrollmentStatus };
        const socket = socketRef.current;
        if (socket?.readyState === WebSocket.OPEN && realtimeStatus === "online") {
            socket.send(JSON.stringify({ type: "analytics.subscribe", filters: params }));
        }
    }, [categoryId, endDate, enrollmentStatus, params, realtimeStatus, startDate]);

    useEffect(() => {
        let active = true;
        setLoading(true);
        apiConfig().get("/analytics/dashboard", { params })
            .then((response) => {
                if (!active) return;
                setSnapshot(response.data.data as DashboardSnapshot);
                setError(null);
            })
            .catch((err) => {
                if (!active) return;
                const message = err?.response?.data?.detail || err?.response?.data?.message || "Não foi possível carregar o dashboard.";
                setError(message);
            })
            .finally(() => active && setLoading(false));
        return () => { active = false; };
    }, [params]);

    useEffect(() => {
        if (!user?.id) return;
        let stopped = false;
        let reconnectTimer: number | null = null;
        let attempt = 0;

        const subscribe = (socket: WebSocket) => {
            const current = filtersRef.current;
            socket.send(JSON.stringify({
                type: "analytics.subscribe",
                filters: {
                    start_date: current.startDate,
                    end_date: current.endDate,
                    ...(current.categoryId ? { category_id: Number(current.categoryId) } : {}),
                    ...(current.enrollmentStatus ? { enrollment_status: current.enrollmentStatus } : {}),
                },
            }));
        };

        const connect = () => {
            if (stopped) return;
            const token = localStorage.getItem("token");
            if (!token) return;
            setRealtimeStatus(attempt ? "reconnecting" : "connecting");
            const socket = new WebSocket(analyticsWsUrl());
            socketRef.current = socket;
            socket.onopen = () => socket.send(JSON.stringify({ type: "auth", token }));
            socket.onmessage = (event) => {
                let payload: { event?: string; data?: DashboardSnapshot; message?: string };
                try { payload = JSON.parse(event.data as string); } catch { return; }
                if (payload.event === "analytics.ready") {
                    attempt = 0;
                    setRealtimeStatus("online");
                    subscribe(socket);
                } else if (payload.event === "analytics.snapshot" && payload.data) {
                    setSnapshot(payload.data);
                    setError(null);
                    setLoading(false);
                } else if (payload.event === "analytics.error") {
                    setError(payload.message ?? "Erro no canal realtime de Analytics.");
                }
            };
            socket.onerror = () => socket.close();
            socket.onclose = () => {
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
            if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
            const socket = socketRef.current;
            socketRef.current = null;
            if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
                socket.close(1000, "analytics session ended");
            }
            setRealtimeStatus("offline");
        };
    }, [user?.id]);

    async function download(format: "csv" | "pdf") {
        setExporting(format);
        setError(null);
        try {
            const response = await apiConfig().get(`/analytics/export.${format}`, {
                params,
                responseType: "blob",
            });
            const url = URL.createObjectURL(response.data);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = `analytics-${startDate}-${endDate}.${format}`;
            document.body.appendChild(anchor);
            anchor.click();
            anchor.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
            setError(message || `Não foi possível exportar ${format.toUpperCase()}.`);
        } finally {
            setExporting(null);
        }
    }

    const kpis = snapshot?.kpis;

    return (
        <section className="mx-auto w-full max-w-7xl px-4 py-8 md:px-8">
            <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
                <div>
                    <p className="text-sm font-semibold uppercase tracking-wide text-primary">Administração</p>
                    <h1 className="text-3xl font-bold text-text">Advanced Analytics</h1>
                    <p className="mt-1 max-w-2xl text-sm text-text-muted">KPIs e gráficos agregados diretamente do PostgreSQL, com filtros, atualização realtime e exportação do recorte atual.</p>
                </div>
                <span className="rounded-pill border border-border px-3 py-1 text-xs text-text-muted" role="status" aria-live="polite">
                    {realtimeStatus === "online" ? "● Realtime conectado" : realtimeStatus === "reconnecting" ? "○ Reconectando" : "○ Conectando"}
                </span>
            </div>

            <Card className="mb-5">
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <label className="text-sm font-medium text-text">Data inicial
                        <input className="base-input mt-1" type="date" value={startDate} max={endDate} onChange={(event) => setStartDate(event.target.value)} />
                    </label>
                    <label className="text-sm font-medium text-text">Data final
                        <input className="base-input mt-1" type="date" value={endDate} min={startDate} onChange={(event) => setEndDate(event.target.value)} />
                    </label>
                    <label className="text-sm font-medium text-text">Categoria
                        <select className="base-input mt-1" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
                            <option value="">Todas</option>
                            {(snapshot?.filter_options.categories ?? []).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
                        </select>
                    </label>
                    <label className="text-sm font-medium text-text">Status da matrícula
                        <select className="base-input mt-1" value={enrollmentStatus} onChange={(event) => setEnrollmentStatus(event.target.value)}>
                            <option value="">Todos</option>
                            {(snapshot?.filter_options.enrollment_statuses ?? ["ativa", "concluida", "cancelada"]).map((status) => <option key={status} value={status}>{status}</option>)}
                        </select>
                    </label>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                    <Button type="button" variant="secondary" loading={exporting === "csv"} onClick={() => void download("csv")}>Exportar CSV</Button>
                    <Button type="button" variant="secondary" loading={exporting === "pdf"} onClick={() => void download("pdf")}>Exportar PDF</Button>
                </div>
            </Card>

            {error && <p role="alert" className="mb-5 rounded-card border border-danger p-3 text-danger">{error}</p>}
            {loading && !snapshot ? <p className="py-10 text-center text-text-muted">Carregando Analytics...</p> : null}

            {snapshot && kpis ? (
                <>
                    <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
                        {[
                            ["Novos usuários", formatNumber(kpis.new_users)],
                            ["Cursos criados", formatNumber(kpis.courses_created)],
                            ["Matrículas", formatNumber(kpis.enrollments)],
                            ["Conclusão", formatPercent(kpis.completion_rate)],
                            ["Avaliação média", kpis.average_rating.toFixed(2)],
                            ["Mensagens", formatNumber(kpis.chat_messages)],
                        ].map(([label, value]) => (
                            <Card key={label} className="p-4">
                                <p className="text-xs text-text-muted">{label}</p>
                                <strong className="mt-1 block text-2xl text-text">{value}</strong>
                            </Card>
                        ))}
                    </div>

                    <div className="grid gap-5 xl:grid-cols-2">
                        <Card className="xl:col-span-2">
                            <h2 className="mb-1 text-lg font-semibold text-text">Atividade diária</h2>
                            <p className="mb-4 text-sm text-text-muted">Line chart interativo de novos cadastros e matrículas.</p>
                            <LineChart data={snapshot.daily_activity} />
                        </Card>
                        <Card>
                            <h2 className="mb-1 text-lg font-semibold text-text">Cursos mais procurados</h2>
                            <p className="mb-4 text-sm text-text-muted">Bar chart por matrículas no recorte atual.</p>
                            <BarChart data={snapshot.top_courses} />
                        </Card>
                        <Card>
                            <h2 className="mb-1 text-lg font-semibold text-text">Status das matrículas</h2>
                            <p className="mb-4 text-sm text-text-muted">Pie chart da distribuição filtrada.</p>
                            <PieChart data={snapshot.enrollment_statuses} />
                        </Card>
                    </div>

                    <p className="mt-4 text-right text-xs text-text-muted">Última agregação: {new Date(snapshot.generated_at).toLocaleString("pt-BR")}</p>
                </>
            ) : null}
        </section>
    );
}
