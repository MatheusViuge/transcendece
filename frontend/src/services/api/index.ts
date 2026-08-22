import { AxiosError } from "axios";
import { toast } from "react-toastify";
import { apiConfig } from "./apiConfig";
import type { ApiEnvelope, IRequest, IRequestBody } from "./types";

type ApiErrorPayload = {
    message?: string;
    detail?: string;
    data?: unknown;
};

function loadingToast(hiddenToast: boolean) {
    return hiddenToast ? undefined : toast.loading("Carregando...");
}

function notifySuccess(hiddenToast: boolean, response: { data?: { message?: string }; statusText?: string }) {
    if (!hiddenToast) {
        toast.success(response.data?.message || response.statusText || "Operação concluída.");
    }
}

function dismissLoading(id: ReturnType<typeof toast.loading> | undefined) {
    if (id !== undefined) toast.dismiss(id);
}

export const api = {
    get: async <TResponse = unknown>({ url, config, hiddenToast = false }: IRequest): Promise<ApiEnvelope<TResponse>> => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().get<ApiEnvelope<TResponse>>(url, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    post: async <TBody, TResponse = unknown>({ url, body, config, hiddenToast = false }: IRequestBody<TBody>): Promise<ApiEnvelope<TResponse>> => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().post<ApiEnvelope<TResponse>>(url, body, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    put: async <TBody, TResponse = unknown>({ url, body, config, hiddenToast = false }: IRequestBody<TBody>): Promise<ApiEnvelope<TResponse>> => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().put<ApiEnvelope<TResponse>>(url, body, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    patch: async <TBody, TResponse = unknown>({ url, body, config, hiddenToast = false }: IRequestBody<TBody>): Promise<ApiEnvelope<TResponse>> => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().patch<ApiEnvelope<TResponse>>(url, body, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    delete: async <TResponse = unknown>({ url, config, hiddenToast = false }: IRequest): Promise<ApiEnvelope<TResponse>> => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().delete<ApiEnvelope<TResponse>>(url, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },
};

export function catchCustom(err: unknown) {
    const error = err as AxiosError<ApiErrorPayload>;
    const payload = error.response?.data;
    const message = payload?.message || (typeof payload?.detail === "string" ? payload.detail : undefined) || error.message;

    toast.error(message || "Ocorreu um erro inesperado.");
}
