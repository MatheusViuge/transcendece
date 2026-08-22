from __future__ import annotations

import hashlib
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile, status


@dataclass(frozen=True)
class FilePolicy:
    extensions: frozenset[str]
    max_bytes: int
    canonical_extension: str


POLICIES: dict[str, FilePolicy] = {
    "image/png": FilePolicy(frozenset({".png"}), 8 * 1024 * 1024, ".png"),
    "image/jpeg": FilePolicy(frozenset({".jpg", ".jpeg"}), 8 * 1024 * 1024, ".jpg"),
    "image/webp": FilePolicy(frozenset({".webp"}), 8 * 1024 * 1024, ".webp"),
    "application/pdf": FilePolicy(frozenset({".pdf"}), 12 * 1024 * 1024, ".pdf"),
    "text/plain": FilePolicy(frozenset({".txt"}), 2 * 1024 * 1024, ".txt"),
}

GENERIC_DECLARED_TYPES = frozenset({"", "application/octet-stream"})
MAX_STREAM_BYTES = max(policy.max_bytes for policy in POLICIES.values())
CHUNK_SIZE = 64 * 1024
_SAFE_DISPLAY = re.compile(r"[^A-Za-z0-9._()\- À-ÿ]+")


def storage_root() -> Path:
    root = Path(os.getenv("FILE_STORAGE_ROOT", "/app/storage/uploads")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def normalize_display_name(filename: str | None) -> str:
    raw = (filename or "arquivo").replace("\\", "/").split("/")[-1].strip()
    clean = _SAFE_DISPLAY.sub("_", raw).strip(" .") or "arquivo"
    return clean[:255]


def _policy_for_extension(extension: str) -> tuple[str, FilePolicy] | None:
    for canonical_type, policy in POLICIES.items():
        if extension in policy.extensions:
            return canonical_type, policy
    return None


def _validate_signature(content_type: str, header: bytes, full_content: bytes | None = None) -> None:
    valid = False
    if content_type == "image/png":
        valid = header.startswith(b"\x89PNG\r\n\x1a\n")
    elif content_type == "image/jpeg":
        valid = header.startswith(b"\xff\xd8\xff")
    elif content_type == "image/webp":
        valid = len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP"
    elif content_type == "application/pdf":
        valid = header.startswith(b"%PDF-")
    elif content_type == "text/plain":
        data = full_content if full_content is not None else header
        try:
            data.decode("utf-8")
            valid = b"\x00" not in data
        except UnicodeDecodeError:
            valid = False

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O conteúdo do arquivo não corresponde ao tipo esperado.",
        )


def validate_declared_file(upload: UploadFile) -> tuple[str, FilePolicy, str]:
    display_name = normalize_display_name(upload.filename)
    extension = Path(display_name).suffix.lower()
    resolved = _policy_for_extension(extension)
    if resolved is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Tipo de arquivo não suportado. Use PNG, JPEG, WebP, PDF ou TXT.",
        )

    canonical_type, policy = resolved
    declared_type = (upload.content_type or "").lower().split(";", 1)[0].strip()

    # Browsers/OSes are allowed to omit MIME metadata or fall back to
    # application/octet-stream. We do not treat that client-provided metadata
    # as authoritative; the real content is still verified by magic bytes/UTF-8
    # before anything is moved into permanent storage.
    if declared_type not in GENERIC_DECLARED_TYPES and declared_type != canonical_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A extensão do arquivo não corresponde ao tipo declarado pelo cliente.",
        )

    return canonical_type, policy, display_name


async def persist_upload(upload: UploadFile) -> dict[str, object]:
    content_type, policy, display_name = validate_declared_file(upload)
    root = storage_root()
    storage_name = f"{uuid.uuid4().hex}{policy.canonical_extension}"
    final_path = (root / storage_name).resolve()
    temp_path = (root / f".{storage_name}.uploading").resolve()

    if root not in final_path.parents or root not in temp_path.parents:
        raise RuntimeError("Storage path escaped configured root")

    size = 0
    digest = hashlib.sha256()
    header = b""
    text_buffer = bytearray() if content_type == "text/plain" else None

    try:
        with temp_path.open("xb") as handle:
            while True:
                chunk = await upload.read(CHUNK_SIZE)
                if not chunk:
                    break
                size += len(chunk)
                if size > policy.max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Arquivo excede o limite de {policy.max_bytes // (1024 * 1024)} MB para este tipo.",
                    )
                if len(header) < 32:
                    header += chunk[: 32 - len(header)]
                if text_buffer is not None:
                    text_buffer.extend(chunk)
                digest.update(chunk)
                handle.write(chunk)

        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Arquivo vazio não é permitido.",
            )

        _validate_signature(content_type, header, bytes(text_buffer) if text_buffer is not None else None)
        temp_path.replace(final_path)
        return {
            "storage_name": storage_name,
            "original_name": display_name,
            "content_type": content_type,
            "size_bytes": size,
            "sha256": digest.hexdigest(),
        }
    except Exception:
        temp_path.unlink(missing_ok=True)
        final_path.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()


def stored_path(storage_name: str) -> Path:
    root = storage_root()
    path = (root / storage_name).resolve()
    if root not in path.parents:
        raise RuntimeError("Storage path escaped configured root")
    return path


def remove_stored_file(storage_name: str) -> None:
    stored_path(storage_name).unlink(missing_ok=True)
