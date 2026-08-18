from passlib.hash import pbkdf2_sha256


def get_password_hash(password: str) -> str:
    """Gera um hash PBKDF2-SHA256 com salt aleatório gerenciado pelo Passlib."""
    return pbkdf2_sha256.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica uma senha em texto contra um hash persistido."""
    try:
        return pbkdf2_sha256.verify(plain_password, hashed_password)
    except (TypeError, ValueError):
        return False
