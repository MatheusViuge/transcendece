import type { IUserStorage } from "@/Context/userContextDefinition";

export type UserRole = IUserStorage["tipo_usuario"];
export type UiPermission =
    | "admin:users:read"
    | "admin:users:write"
    | "admin:roles:write"
    | "courses:manage"
    | "enrollments:self";

const ROLE_BASE_PATHS: Record<UserRole, string> = {
    aluno: "/aluno",
    instrutor: "/instrutor",
    admin: "/admin",
};

export const ROLE_LABELS: Record<UserRole, string> = {
    aluno: "Aluno",
    instrutor: "Instrutor",
    admin: "Administrador",
};

export const ROLE_NAV_LINKS: Record<UserRole, Array<{ label: string; to: string }>> = {
    aluno: [
        { label: "Explorar", to: "/aluno/explorar" },
        { label: "Meus cursos", to: "/aluno/cursos" },
        { label: "Arquivos", to: "/aluno/arquivos" },
    ],
    instrutor: [
        { label: "Meus Cursos", to: "/instrutor/cursos" },
        { label: "Correções", to: "/instrutor/correcoes" },
        { label: "Arquivos", to: "/instrutor/arquivos" },
    ],
    admin: [
        { label: "Usuários", to: "/admin/usuarios" },
        { label: "Cursos", to: "/admin/cursos" },
        { label: "Arquivos", to: "/admin/arquivos" },
    ],
};

const UI_PERMISSIONS: Record<UserRole, ReadonlySet<UiPermission>> = {
    aluno: new Set(["enrollments:self"]),
    instrutor: new Set(["courses:manage"]),
    admin: new Set(["admin:users:read", "admin:users:write", "admin:roles:write", "courses:manage"]),
};

const roleEntries = Object.entries(ROLE_BASE_PATHS) as Array<[UserRole, string]>;

export function hasUiPermission(role: UserRole | undefined, permission: UiPermission): boolean {
    return role ? UI_PERMISSIONS[role].has(permission) : false;
}

export function getRequiredRole(pathname: string): UserRole | null {
    const match = roleEntries.find(
        ([, basePath]) => pathname === basePath || pathname.startsWith(`${basePath}/`),
    );

    return match?.[0] ?? null;
}

export function getRoleLandingPath(role: UserRole): string {
    return ROLE_BASE_PATHS[role];
}
