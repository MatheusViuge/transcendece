import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Modal } from "@/design-system/components/Modal";
import { api, catchCustom } from "@/services/api";
import { apiConfig } from "@/services/api/apiConfig";

const FILE_POLICIES: Record<string, number> = {
    "image/png": 8 * 1024 * 1024,
    "image/jpeg": 8 * 1024 * 1024,
    "image/webp": 8 * 1024 * 1024,
    "application/pdf": 12 * 1024 * 1024,
    "text/plain": 2 * 1024 * 1024,
};

const ACCEPT = ".png,.jpg,.jpeg,.webp,.pdf,.txt";

type StoredFile = {
    id: number;
    original_name: string;
    content_type: string;
    size_bytes: number;
    sha256: string;
    purpose: string;
    created_at: string;
    content_url: string;
};

type PreviewState = {
    url?: string;
    text?: string;
    type: string;
    name: string;
};

function prettySize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function validateFile(file: File): string | null {
    const limit = FILE_POLICIES[file.type];
    if (!limit) return "Tipo não suportado. Use PNG, JPEG, WebP, PDF ou TXT.";
    if (file.size === 0) return "Arquivo vazio não é permitido.";
    if (file.size > limit) return `Arquivo excede o limite de ${Math.floor(limit / 1024 / 1024)} MB.`;
    return null;
}

export default function Files() {
    const [files, setFiles] = useState<StoredFile[]>([]);
    const [selected, setSelected] = useState<File | null>(null);
    const [selectedPreview, setSelectedPreview] = useState<string | null>(null);
    const [preview, setPreview] = useState<PreviewState | null>(null);
    const [progress, setProgress] = useState(0);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [reloadKey, setReloadKey] = useState(0);
    const previewRef = useRef<string | null>(null);
    const selectedPreviewRef = useRef<string | null>(null);

    useEffect(() => {
        let active = true;
        async function loadFiles() {
            try {
                const response = await api.get<StoredFile[]>({ url: "/files", hiddenToast: true });
                if (active) setFiles(response.data ?? []);
            } catch (err) {
                if (active) catchCustom(err);
            }
        }
        void loadFiles();
        return () => {
            active = false;
        };
    }, [reloadKey]);

    useEffect(() => () => {
        if (previewRef.current) URL.revokeObjectURL(previewRef.current);
        if (selectedPreviewRef.current) URL.revokeObjectURL(selectedPreviewRef.current);
    }, []);

    function chooseFile(file: File | null) {
        if (selectedPreviewRef.current) URL.revokeObjectURL(selectedPreviewRef.current);
        selectedPreviewRef.current = null;
        setSelectedPreview(null);
        setError(null);
        setSelected(null);
        setProgress(0);
        if (!file) return;

        const validation = validateFile(file);
        if (validation) {
            setError(validation);
            return;
        }

        setSelected(file);
        if (file.type.startsWith("image/") || file.type === "application/pdf") {
            const url = URL.createObjectURL(file);
            selectedPreviewRef.current = url;
            setSelectedPreview(url);
        }
    }

    async function upload() {
        if (!selected) return;
        setUploading(true);
        setError(null);
        setProgress(0);
        try {
            const form = new FormData();
            form.append("file", selected);
            form.append("purpose", "manual-test");
            await apiConfig().post("/files", form, {
                headers: { "Content-Type": "multipart/form-data" },
                onUploadProgress: (event) => {
                    if (!event.total) return;
                    setProgress(Math.min(100, Math.round((event.loaded * 100) / event.total)));
                },
            });
            chooseFile(null);
            setReloadKey((value) => value + 1);
        } catch (err) {
            setError("O servidor rejeitou o upload. Confira formato e tamanho.");
            catchCustom(err);
        } finally {
            setUploading(false);
        }
    }

    async function fetchBlob(item: StoredFile) {
        const response = await apiConfig().get(`/files/${item.id}/content`, { responseType: "blob" });
        return response.data as Blob;
    }

    async function openPreview(item: StoredFile) {
        try {
            const blob = await fetchBlob(item);
            if (previewRef.current) URL.revokeObjectURL(previewRef.current);
            previewRef.current = null;

            if (item.content_type === "text/plain") {
                setPreview({ text: await blob.text(), type: item.content_type, name: item.original_name });
                return;
            }

            const url = URL.createObjectURL(blob);
            previewRef.current = url;
            setPreview({ url, type: item.content_type, name: item.original_name });
        } catch (err) {
            catchCustom(err);
        }
    }

    async function download(item: StoredFile) {
        try {
            const response = await apiConfig().get(`/files/${item.id}/content?download=true`, { responseType: "blob" });
            const url = URL.createObjectURL(response.data);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = item.original_name;
            document.body.appendChild(anchor);
            anchor.click();
            anchor.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            catchCustom(err);
        }
    }

    async function remove(item: StoredFile) {
        if (!window.confirm(`Excluir ${item.original_name}?`)) return;
        try {
            await api.delete({ url: `/files/${item.id}`, hiddenToast: true });
            setFiles((current) => current.filter((file) => file.id !== item.id));
        } catch (err) {
            catchCustom(err);
        }
    }

    function closePreview() {
        if (previewRef.current) URL.revokeObjectURL(previewRef.current);
        previewRef.current = null;
        setPreview(null);
    }

    return (
        <section className="mx-auto w-full max-w-5xl px-4 py-10 md:px-8">
            <div className="mb-8">
                <p className="text-sm font-semibold uppercase tracking-wide text-primary">File Upload & Management</p>
                <h1 className="mt-2 text-3xl font-bold text-text">Meus arquivos</h1>
                <p className="mt-2 max-w-2xl text-text-muted">Envie PNG, JPEG, WebP, PDF ou TXT. Os arquivos ficam privados e vinculados à sua conta.</p>
            </div>

            <Card className="mb-8 p-6">
                <label htmlFor="file-upload" className="mb-2 block font-semibold text-text">Selecionar arquivo</label>
                <input
                    id="file-upload"
                    type="file"
                    accept={ACCEPT}
                    disabled={uploading}
                    onChange={(event) => chooseFile(event.target.files?.[0] ?? null)}
                    className="base-input w-full"
                />
                {error && <p role="alert" className="mt-3 text-sm text-danger">{error}</p>}

                {selected && (
                    <div className="mt-5 rounded-card border border-border bg-surface-subtle p-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <strong className="block text-text">{selected.name}</strong>
                                <span className="text-sm text-text-muted">{selected.type} · {prettySize(selected.size)}</span>
                            </div>
                            <Button type="button" onClick={upload} loading={uploading}>Enviar arquivo</Button>
                        </div>
                        {selectedPreview && selected.type.startsWith("image/") && (
                            <img src={selectedPreview} alt={`Preview de ${selected.name}`} className="mt-4 max-h-64 rounded-card object-contain" />
                        )}
                        {selectedPreview && selected.type === "application/pdf" && (
                            <iframe title={`Preview de ${selected.name}`} src={selectedPreview} className="mt-4 h-64 w-full rounded-card border border-border" />
                        )}
                        {selected.type === "text/plain" && (
                            <p className="mt-4 text-sm text-text-muted">TXT selecionado. O conteúdo será validado como UTF-8 pelo servidor.</p>
                        )}
                        {(uploading || progress > 0) && (
                            <div className="mt-4">
                                <div className="mb-1 flex justify-between text-sm text-text-muted"><span>Progresso</span><span>{progress}%</span></div>
                                <progress value={progress} max={100} className="h-3 w-full" aria-label={`Upload ${progress}% concluído`} />
                            </div>
                        )}
                    </div>
                )}
            </Card>

            <div className="space-y-3">
                <h2 className="text-xl font-semibold text-text">Arquivos enviados</h2>
                {files.length === 0 ? (
                    <Card className="p-6 text-text-muted">Nenhum arquivo enviado ainda.</Card>
                ) : files.map((item) => (
                    <Card key={item.id} className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
                        <div className="min-w-0">
                            <strong className="block truncate text-text">{item.original_name}</strong>
                            <span className="text-sm text-text-muted">{item.content_type} · {prettySize(item.size_bytes)}</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            <Button type="button" variant="secondary" onClick={() => openPreview(item)}>Visualizar</Button>
                            <Button type="button" variant="secondary" onClick={() => download(item)}>Baixar</Button>
                            <Button type="button" variant="danger" onClick={() => remove(item)}>Excluir</Button>
                        </div>
                    </Card>
                ))}
            </div>

            <Modal open={preview !== null} title={preview?.name ?? "Preview"} onClose={closePreview}>
                {preview?.url && preview.type.startsWith("image/") && <img src={preview.url} alt={preview.name} className="max-h-[65vh] w-full object-contain" />}
                {preview?.url && preview.type === "application/pdf" && <iframe title={preview.name} src={preview.url} className="h-[65vh] w-full border-0" />}
                {preview?.type === "text/plain" && <pre className="max-h-[65vh] overflow-auto whitespace-pre-wrap rounded-card bg-surface-subtle p-4 text-sm text-text">{preview.text}</pre>}
            </Modal>
        </section>
    );
}
