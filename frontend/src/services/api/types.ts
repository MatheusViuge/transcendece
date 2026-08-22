import type { AxiosRequestConfig } from "axios";

export interface ApiEnvelope<T> {
    data: T;
    message: string;
}

export interface IRequest {
    url: string;
    config?: AxiosRequestConfig;
    hiddenToast?: boolean;
}

export interface IRequestBody<T> {
    url: string;
    body?: T;
    config?: AxiosRequestConfig;
    hiddenToast?: boolean;
}
