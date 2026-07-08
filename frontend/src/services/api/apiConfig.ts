import axios from "axios";

export function apiConfig() {
    const baseURL = import.meta.env.VITE_API_URL;

    const api = axios.create({
        baseURL,
        headers: {
            "Content-Type": "application/json;charset=utf-8",
        }
    });

    api.interceptors.request.use((config) => {
        const token = localStorage.getItem('token') || '';

        if (token)
            config.headers.Authorization = "Bearer " + token;
        return config;
    } )

    return api;
}
