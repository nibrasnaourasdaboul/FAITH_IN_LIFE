"""Generate SQLAlchemy models from FAITH in LIFE Diagrams/ERD ER Diagram/FAITH_in_LIFE_ERD.dbml.

Run from the repository root:
    python backend/scripts/generate_models.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DBML = ROOT / "FAITH in LIFE Diagrams/ERD ER Diagram/FAITH_in_LIFE_ERD.dbml"
OUT = ROOT / "backend" / "app" / "models" / "entities.py"

RESERVED = {"user", "references", "session", "order", "group"}

FORCE_REQUIRED = {
    ("User", "email"),
    ("User", "password_hash"),
    ("User", "full_name"),
    ("User", "account_status"),
    ("User", "mfa_enabled"),
    ("Role", "role_code"),
    ("Role", "role_name"),
}

PROFILE_TABLES = {
    "PatientProfile",
    "DoctorProfile",
    "GuardianProfile",
    "AdminProfile",
    "NotificationPreference",
}

# The grouped DBML already declares these relationships in Ref lines.
EXTRA_FKS: dict[tuple[str, str], tuple[str, str]] = {}

UNIQUE_PAIRS = {
    "UserRole": ("user_id", "role_id"),
    "RolePermission": ("role_id", "permission_id"),
    "PatientGuardianLink": ("patient_id", "guardian_id"),
    "ExerciseCategoryLink": ("exercise_id", "category_id"),
    "PatientBadge": ("patient_id", "badge_id"),
    "ReportSession": ("smart_report_id", "session_id"),
}

TEXT_HINTS = (
    "description",
    "notes",
    "text",
    "summary",
    "payload",
    "rationale",
    "details",
    "message",
    "content",
    "findings",
    "impression",
    "guidance",
    "instructions",
    "complaint",
    "factors",
    "disclaimer",
    "criteria",
    "highlights",
    "changes",
    "evidence",
    "warning",
    "body",
    "question",
    "answer",
    "reason",
    "uri",
    "url",
    "citation",
    "history",
    "tips",
    "filter",
    "edits",
    "signs",
    "curve",
    "template",
    "hash",
)

TYPE_MAP = {
    "uuid": "uuid",
    "string": "string",
    "boolean": "bool",
    "datetime": "datetime",
    "date": "date",
    "int": "int",
    "float": "float",
    "time": "time",
}


def snake(name: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def table_name(class_name: str) -> str:
    s = snake(class_name)
    if s.endswith("y") and len(s) > 1 and s[-2] not in "aeiou":
        plural = s[:-1] + "ies"
    elif s.endswith(("s", "x", "ch", "sh")):
        plural = s + "es"
    else:
        plural = s + "s"
    if plural in RESERVED or s in RESERVED:
        plural = plural if plural.endswith("s") else plural + "s"
    return plural


def parse_dbml(text: str) -> tuple[dict[str, list[dict]], dict[tuple[str, str], tuple[str, str, bool]]]:
    tables: dict[str, list[dict]] = {}
    current: str | None = None
    fks: dict[tuple[str, str], tuple[str, str, bool]] = {}
    text = re.sub(r"indexes\s*\{[^}]*\}", "", text, flags=re.S)

    for raw in text.splitlines():
        line = raw.split("//")[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r"Table\s+(\w+)\s+\{", line)
        if m:
            current = m.group(1)
            tables[current] = []
            continue
        if line.strip() == "}":
            current = None
            continue
        if current:
            col = re.match(r"\s*(\w+)\s+(\w+)(?:\s+\[(.*)\])?", line)
            if not col:
                continue
            name, typ, attrs = col.group(1), col.group(2), col.group(3) or ""
            tables[current].append(
                {
                    "name": name,
                    "type": typ,
                    "pk": "pk" in attrs.split(),
                    "unique": "unique" in attrs.split(),
                }
            )
            continue
        ref = re.match(r"Ref:\s+(\w+)\.(\w+)\s+([>\-])\s+(\w+)\.(\w+)", line)
        if ref:
            src_t, src_c, op, dst_t, dst_c = ref.groups()
            fks[(src_t, src_c)] = (dst_t, dst_c, op == "-")

    for key, target in EXTRA_FKS.items():
        fks.setdefault(key, (target[0], target[1], False))
    return tables, fks


def py_type(col: dict, optional: bool) -> str:
    kind = TYPE_MAP.get(col["type"], "string")
    base = {
        "uuid": "uuid.UUID",
        "string": "str",
        "bool": "bool",
        "datetime": "datetime",
        "date": "date",
        "int": "int",
        "float": "float",
        "time": "time",
    }[kind]
    return f"{base} | None" if optional else base


def sa_type(col: dict) -> str:
    kind = col["type"]
    if kind == "uuid":
        return "Uuid(as_uuid=True)"
    if kind == "boolean":
        return "Boolean"
    if kind == "datetime":
        return "DateTime(timezone=True)"
    if kind == "date":
        return "Date"
    if kind == "time":
        return "Time"
    if kind == "int":
        return "Integer"
    if kind == "float":
        return "Float"
    name = col["name"]
    if name in {"email", "phone", "password_hash", "token_hash", "license_number", "national_id", "full_name"}:
        return "String(255)"
    if any(h in name for h in TEXT_HINTS) or name.endswith("_notes"):
        return "Text"
    return "String(255)"


def render(tables: dict[str, list[dict]], fks: dict) -> str:
    lines: list[str] = [
        '"""SQLAlchemy models generated from FAITH in LIFE Diagrams/ERD ER Diagram/FAITH_in_LIFE_ERD.dbml.',
        "",
        "Do not edit by hand. Regenerate with backend/scripts/generate_models.py.",
        "User gains email verification, locale, and avatar fields required by the",
        "account-management flows. EmbeddingIndex.embedding is JSON because",
        "pgvector is not installed on this PostgreSQL server.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import uuid",
        "from datetime import date, datetime, time",
        "",
        "from sqlalchemy import (",
        "    Boolean,",
        "    Date,",
        "    DateTime,",
        "    Float,",
        "    ForeignKey,",
        "    Integer,",
        "    JSON,",
        "    String,",
        "    Text,",
        "    Time,",
        "    UniqueConstraint,",
        "    Uuid,",
        ")",
        "from sqlalchemy.orm import Mapped, mapped_column",
        "",
        "from app.db.base import Base",
        "",
        "",
    ]

    names = {name: table_name(name) for name in tables}

    for class_name, cols in tables.items():
        tname = names[class_name]
        lines.append(f"class {class_name}(Base):")
        lines.append(f'    __tablename__ = "{tname}"')
        if class_name in UNIQUE_PAIRS:
            a, b = UNIQUE_PAIRS[class_name]
            lines.append(
                f'    __table_args__ = (UniqueConstraint("{a}", "{b}", name="uq_{tname}_{a}_{b}"),)'
            )
        lines.append("")
        for col in cols:
            optional = not col["pk"]
            fk = fks.get((class_name, col["name"]))
            unique = col["unique"] or (fk is not None and fk[2])
            if class_name in PROFILE_TABLES and col["name"] == "user_id":
                optional = False
                unique = True
            if (class_name, col["name"]) in FORCE_REQUIRED:
                optional = False
            mapped = py_type(col, optional)
            args = [sa_type(col)]
            if fk:
                dst_table = names[fk[0]]
                ondelete = "CASCADE" if col["name"].endswith("_id") else "SET NULL"
                args.append(f'ForeignKey("{dst_table}.{fk[1]}", ondelete="{ondelete}")')
            kwargs = []
            if col["pk"]:
                kwargs.append("primary_key=True")
                kwargs.append("default=uuid.uuid4")
            if unique and not col["pk"]:
                kwargs.append("unique=True")
            if optional:
                kwargs.append("nullable=True")
            else:
                kwargs.append("nullable=False")
            if fk or col["name"].endswith("_id"):
                kwargs.append("index=True")
            if col["type"] == "boolean" and not col["pk"]:
                kwargs.append("default=False")
            joined = ", ".join(args + kwargs)
            lines.append(f"    {col['name']}: Mapped[{mapped}] = mapped_column({joined})")

        if class_name == "User":
            lines.append(
                "    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)"
            )
            lines.append(
                '    preferred_locale: Mapped[str] = mapped_column(String(8), default="ar", nullable=False)'
            )
            lines.append(
                "    avatar_uri: Mapped[str | None] = mapped_column(Text, nullable=True)"
            )
        if class_name == "EmbeddingIndex":
            lines.append(
                "    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)"
            )
        lines.append("")
        lines.append("")

    lines.append("__all__ = [")
    for name in tables:
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    tables, fks = parse_dbml(DBML.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(tables, fks), encoding="utf-8")
    print(f"Wrote {len(tables)} models to {OUT}")


if __name__ == "__main__":
    main()
