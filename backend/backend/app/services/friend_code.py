from __future__ import annotations

import re
import secrets

FRIEND_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
FRIEND_CODE_CHARS = 10
FRIEND_CODE_PATTERN = re.compile(r"^[A-Z2-9]{5}-[A-Z2-9]{5}$")


def generate_friend_code() -> str:
    raw = "".join(secrets.choice(FRIEND_CODE_ALPHABET) for _ in range(FRIEND_CODE_CHARS))
    return f"{raw[:5]}-{raw[5:]}"


def normalize_friend_code(value: str) -> str | None:
    compact = re.sub(r"[^A-Z0-9]", "", value.upper())
    if len(compact) != FRIEND_CODE_CHARS:
        return None
    formatted = f"{compact[:5]}-{compact[5:]}"
    return formatted if FRIEND_CODE_PATTERN.fullmatch(formatted) else None
