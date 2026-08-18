import { AxiosError } from "axios";
import { toast } from "react-toastify";
import { apiConfig } from "./apiConfig";
import type { IRequest, IRequestBody } from "./types";

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
    get: async ({ url, config, hiddenToast = false }: IRequest) => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().get(url, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    post: async <T>({ url, body, config, hiddenToast = false }: IRequestBody<T>) => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().post(url, body, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    put: async <T>({ url, body, config, hiddenToast = false }: IRequestBody<T>) => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().put(url, body, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    patch: async <T>({ url, body, config, hiddenToast = false }: IRequestBody<T>) => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().patch(url, body, config);
            notifySuccess(hiddenToast, response);
            return response.data;
        } finally {
            dismissLoading(loading);
        }
    },

    delete: async ({ url, config, hiddenToast = false }: IRequest) => {
        const loading = loadingToast(hiddenToast);

        try {
            const response = await apiConfig().delete(url, config);
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
