import type { IUserStorage } from "@/Context/userContextDefinition";

export type UserRole = IUserStorage["tipo_usuario"];

const ROLE_BASE_PATHS: Record<UserRole, string> = {
    aluno: "/aluno",
    instrutor: "/instrutor",
    admin: "/admin",
};

const roleEntries = Object.entries(ROLE_BASE_PATHS) as Array<[UserRole, string]>;

export function getRequiredRole(pathname: string): UserRole | null {
    const match = roleEntries.find(
        ([, basePath]) => pathname === basePath || pathname.startsWith(`${basePath}/`),
    );

    return match?.[0] ?? null;
}

export function getRoleLandingPath(role: UserRole): string {
    return ROLE_BASE_PATHS[role];
}
