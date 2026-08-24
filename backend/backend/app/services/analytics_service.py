from __future__ import annotations

import csv
import io
import json
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Categoria
from app.models.chat import ChatMessage
from app.models.course import Curso
from app.models.enrollment import Matricula
from app.models.evaluation import AvaliacaoCurso
from app.models.user import Usuario

DEFAULT_RANGE_DAYS = 30
ALLOWED_ENROLLMENT_STATUSES = {"ativa", "concluida", "cancelada"}


@dataclass(frozen=True)
class AnalyticsFilters:
    start_date: date
    end_date: date
    category_id: int | None = None
    enrollment_status: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "category_id": self.category_id,
            "enrollment_status": self.enrollment_status,
        }


def resolve_filters(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    enrollment_status: str | None = None,
) -> AnalyticsFilters:
    today = datetime.now(timezone.utc).date()
    resolved_end = end_date or today
    resolved_start = start_date or (resolved_end - timedelta(days=DEFAULT_RANGE_DAYS - 1))
    if resolved_start > resolved_end:
        raise ValueError("start_date não pode ser posterior a end_date.")
    if (resolved_end - resolved_start).days > 366:
        raise ValueError("O intervalo máximo do dashboard é de 367 dias.")
    if category_id is not None and category_id < 1:
        raise ValueError("category_id deve ser positivo.")
    if enrollment_status is not None:
        normalized_status = enrollment_status.strip().lower()
        if normalized_status not in ALLOWED_ENROLLMENT_STATUSES:
            raise ValueError("Status de matrícula inválido.")
        enrollment_status = normalized_status
    return AnalyticsFilters(
        start_date=resolved_start,
        end_date=resolved_end,
        category_id=category_id,
        enrollment_status=enrollment_status,
    )


def filters_from_payload(payload: object) -> AnalyticsFilters:
    if not isinstance(payload, dict):
        raise ValueError("Filtros inválidos.")

    def parse_date(key: str) -> date | None:
        value = payload.get(key)
        if value in (None, ""):
            return None
        if not isinstance(value, str):
            raise ValueError(f"{key} inválido.")
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{key} inválido.") from exc

    raw_category = payload.get("category_id")
    category_id: int | None = None
    if raw_category not in (None, ""):
        try:
            category_id = int(raw_category)
        except (TypeError, ValueError) as exc:
            raise ValueError("category_id inválido.") from exc

    raw_status = payload.get("enrollment_status")
    enrollment_status = None if raw_status in (None, "") else str(raw_status)
    return resolve_filters(
        start_date=parse_date("start_date"),
        end_date=parse_date("end_date"),
        category_id=category_id,
        enrollment_status=enrollment_status,
    )


def _bounds(filters: AnalyticsFilters) -> tuple[datetime, datetime]:
    start = datetime.combine(filters.start_date, time.min)
    end_exclusive = datetime.combine(filters.end_date + timedelta(days=1), time.min)
    return start, end_exclusive


def _day_key(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.date().isoformat()


def build_dashboard(db: Session, filters: AnalyticsFilters) -> dict[str, object]:
    start, end_exclusive = _bounds(filters)

    category_query = db.query(Categoria).order_by(Categoria.nome.asc())
    categories = category_query.all()
    if filters.category_id is not None and not any(item.id == filters.category_id for item in categories):
        raise ValueError("Categoria não encontrada.")

    category_course_ids_query = db.query(Curso.id)
    if filters.category_id is not None:
        category_course_ids_query = category_course_ids_query.filter(Curso.categoria_id == filters.category_id)
    category_course_ids = [row[0] for row in category_course_ids_query.all()]

    courses_query = db.query(Curso).filter(
        Curso.data_criacao >= start,
        Curso.data_criacao < end_exclusive,
    )
    if filters.category_id is not None:
        courses_query = courses_query.filter(Curso.categoria_id == filters.category_id)
    courses_created = courses_query.count()

    user_rows = (
        db.query(Usuario.data_cadastro)
        .filter(Usuario.data_cadastro >= start, Usuario.data_cadastro < end_exclusive)
        .all()
    )

    enrollments_query = db.query(Matricula).filter(
        Matricula.data_matricula >= start,
        Matricula.data_matricula < end_exclusive,
    )
    if filters.category_id is not None:
        if category_course_ids:
            enrollments_query = enrollments_query.filter(Matricula.curso_id.in_(category_course_ids))
        else:
            enrollments_query = enrollments_query.filter(Matricula.id == -1)
    if filters.enrollment_status is not None:
        enrollments_query = enrollments_query.filter(
            Matricula.status_matricula == filters.enrollment_status
        )
    enrollment_rows = enrollments_query.all()

    completed = sum(1 for item in enrollment_rows if item.status_matricula == "concluida")
    completion_rate = round((completed / len(enrollment_rows)) * 100, 2) if enrollment_rows else 0.0

    ratings_query = db.query(AvaliacaoCurso).filter(
        AvaliacaoCurso.data_criacao >= start,
        AvaliacaoCurso.data_criacao < end_exclusive,
    )
    if filters.category_id is not None:
        if category_course_ids:
            ratings_query = ratings_query.filter(AvaliacaoCurso.curso_id.in_(category_course_ids))
        else:
            ratings_query = ratings_query.filter(AvaliacaoCurso.id == -1)
    rating_rows = ratings_query.all()
    average_rating = (
        round(sum(item.nota for item in rating_rows) / len(rating_rows), 2)
        if rating_rows
        else 0.0
    )

    chat_messages = db.query(ChatMessage).filter(
        ChatMessage.created_at >= start,
        ChatMessage.created_at < end_exclusive,
    ).count()

    day_counts: dict[str, dict[str, int]] = {}
    cursor = filters.start_date
    while cursor <= filters.end_date:
        day_counts[cursor.isoformat()] = {"registrations": 0, "enrollments": 0}
        cursor += timedelta(days=1)

    for (registered_at,) in user_rows:
        key = _day_key(registered_at)
        if key in day_counts:
            day_counts[key]["registrations"] += 1
    for enrollment in enrollment_rows:
        key = _day_key(enrollment.data_matricula)
        if key in day_counts:
            day_counts[key]["enrollments"] += 1

    course_counts: dict[int, int] = {}
    for enrollment in enrollment_rows:
        course_counts[enrollment.curso_id] = course_counts.get(enrollment.curso_id, 0) + 1
    course_names = {
        item.id: item.titulo
        for item in db.query(Curso).filter(Curso.id.in_(course_counts.keys())).all()
    } if course_counts else {}
    top_courses = [
        {"course_id": course_id, "label": course_names.get(course_id, f"Curso {course_id}"), "value": count}
        for course_id, count in sorted(
            course_counts.items(),
            key=lambda pair: (-pair[1], course_names.get(pair[0], "")),
        )[:8]
    ]

    status_counts = {status: 0 for status in sorted(ALLOWED_ENROLLMENT_STATUSES)}
    for enrollment in enrollment_rows:
        status_counts.setdefault(enrollment.status_matricula, 0)
        status_counts[enrollment.status_matricula] += 1
    enrollment_statuses = [
        {"label": status, "value": value}
        for status, value in status_counts.items()
        if value > 0
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "filters": filters.as_dict(),
        "filter_options": {
            "categories": [{"id": item.id, "name": item.nome} for item in categories],
            "enrollment_statuses": sorted(ALLOWED_ENROLLMENT_STATUSES),
        },
        "kpis": {
            "new_users": len(user_rows),
            "courses_created": courses_created,
            "enrollments": len(enrollment_rows),
            "completion_rate": completion_rate,
            "average_rating": average_rating,
            "chat_messages": chat_messages,
        },
        "daily_activity": [
            {"date": key, **counts} for key, counts in day_counts.items()
        ],
        "top_courses": top_courses,
        "enrollment_statuses": enrollment_statuses,
    }


def dashboard_fingerprint(snapshot: dict[str, object]) -> str:
    comparable = dict(snapshot)
    comparable.pop("generated_at", None)
    return json.dumps(comparable, sort_keys=True, ensure_ascii=False, default=str)


def dashboard_to_csv(snapshot: dict[str, object]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    filters = snapshot["filters"]
    kpis = snapshot["kpis"]

    writer.writerow(["Advanced Analytics Dashboard"])
    writer.writerow(["start_date", filters["start_date"]])
    writer.writerow(["end_date", filters["end_date"]])
    writer.writerow(["category_id", filters["category_id"] or "all"])
    writer.writerow(["enrollment_status", filters["enrollment_status"] or "all"])
    writer.writerow([])
    writer.writerow(["metric", "value"])
    for key, value in kpis.items():
        writer.writerow([key, value])

    writer.writerow([])
    writer.writerow(["daily_activity"])
    writer.writerow(["date", "registrations", "enrollments"])
    for row in snapshot["daily_activity"]:
        writer.writerow([row["date"], row["registrations"], row["enrollments"]])

    writer.writerow([])
    writer.writerow(["top_courses"])
    writer.writerow(["course_id", "course", "enrollments"])
    for row in snapshot["top_courses"]:
        writer.writerow([row["course_id"], row["label"], row["value"]])

    writer.writerow([])
    writer.writerow(["enrollment_statuses"])
    writer.writerow(["status", "count"])
    for row in snapshot["enrollment_statuses"]:
        writer.writerow([row["label"], row["value"]])

    return output.getvalue().encode("utf-8-sig")


def _pdf_ascii(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def dashboard_to_pdf(snapshot: dict[str, object]) -> bytes:
    filters = snapshot["filters"]
    kpis = snapshot["kpis"]
    lines = [
        "Advanced Analytics Dashboard",
        f"Periodo: {filters['start_date']} a {filters['end_date']}",
        f"Categoria: {filters['category_id'] or 'todas'}",
        f"Status de matricula: {filters['enrollment_status'] or 'todos'}",
        "",
        "KPIs",
        f"Novos usuarios: {kpis['new_users']}",
        f"Cursos criados: {kpis['courses_created']}",
        f"Matriculas: {kpis['enrollments']}",
        f"Taxa de conclusao: {kpis['completion_rate']}%",
        f"Avaliacao media: {kpis['average_rating']}",
        f"Mensagens de chat: {kpis['chat_messages']}",
        "",
        "Top cursos por matricula",
    ]
    for row in snapshot["top_courses"][:8]:
        lines.append(f"- {row['label']}: {row['value']}")
    if not snapshot["top_courses"]:
        lines.append("- sem matriculas no recorte")

    content_parts = ["BT", "/F1 15 Tf", "50 790 Td"]
    for index, line in enumerate(lines):
        if index == 1:
            content_parts.extend(["/F1 10 Tf"])
        content_parts.append(f"({_pdf_ascii(line)}) Tj")
        content_parts.append("0 -20 Td")
    content_parts.append("ET")
    stream = "\n".join(content_parts).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)
