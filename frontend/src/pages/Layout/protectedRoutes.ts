export const protectedBasePaths = ["/instrutor", "/aluno", "/admin"] as const;

export function isProtectedPath(pathname: string): boolean {
    return protectedBasePaths.some(
        (path) => pathname === path || pathname.startsWith(`${path}/`),
    );
}
