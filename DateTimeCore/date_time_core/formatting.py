"""Shared datetime formatting helpers for the ecosystem."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Tuple

from .constants import RUN_ID_TIMESTAMP_FORMAT


def utc_now() -> datetime:
    """Return the current UTC datetime as a timezone-aware object."""
    return datetime.now(timezone.utc)


def ensure_timezone(value: datetime, *, default_timezone: timezone = timezone.utc) -> datetime:
    """Return a timezone-aware datetime.

    Naive datetimes are treated as UTC by default because SharedCode uses UTC as
    the technical timestamp baseline.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=default_timezone)

    return value


def datetime_to_utc_iso(value: datetime) -> str:
    """Return a datetime normalized to UTC using compact ISO-8601 notation.

    Standard output example: 2026-06-30T15:04:05Z
    """
    normalized = ensure_timezone(value).astimezone(timezone.utc)
    return normalized.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def datetime_to_local_iso(value: datetime) -> str:
    """Return a datetime normalized to the workstation local timezone.

    Standard output example: 2026-06-30T12:04:05-03:00
    """
    normalized = ensure_timezone(value).astimezone()
    return normalized.replace(microsecond=0).isoformat()


def utc_now_iso() -> str:
    """Return the current UTC timestamp in the SharedCode JSON format."""
    return datetime_to_utc_iso(utc_now())


def local_now_iso() -> str:
    """Return the current local timestamp in ISO-8601 format."""
    return datetime_to_local_iso(utc_now())


def create_timestamp_pair() -> tuple[str, str]:
    """Return UTC and local timestamp strings that represent the same instant."""
    now_utc = utc_now().replace(microsecond=0)
    return datetime_to_utc_iso(now_utc), datetime_to_local_iso(now_utc)


def parse_iso_datetime(value: str, *, default_timezone: timezone = timezone.utc) -> datetime:
    """Parse a common ISO-8601 datetime string.

    Supports both UTC forms used in Python ecosystems:
    - 2026-06-30T15:04:05Z
    - 2026-06-30T15:04:05+00:00
    """
    normalized = str(value).strip()
    if not normalized:
        raise ValueError("Datetime value cannot be empty.")

    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"

    parsed = datetime.fromisoformat(normalized)
    return ensure_timezone(parsed, default_timezone=default_timezone)


def timestamp_seconds_to_utc_iso(value: float | int) -> str:
    """Convert POSIX timestamp seconds to the SharedCode UTC ISO format."""
    return datetime_to_utc_iso(datetime.fromtimestamp(float(value), timezone.utc))


def timestamp_seconds_to_local_iso(value: float | int) -> str:
    """Convert POSIX timestamp seconds to the workstation local ISO format."""
    return datetime_to_local_iso(datetime.fromtimestamp(float(value), timezone.utc))


def datetime_to_run_id_timestamp(value: datetime) -> str:
    """Return the UTC timestamp fragment used by run identifiers."""
    normalized = ensure_timezone(value).astimezone(timezone.utc)
    return normalized.strftime(RUN_ID_TIMESTAMP_FORMAT)


def format_utc_offset(value: datetime) -> str:
    """Return a datetime UTC offset using +HH:MM or -HH:MM notation."""
    offset = ensure_timezone(value).strftime("%z")
    if not offset:
        return ""

    return f"{offset[:3]}:{offset[3:]}"


def format_iso_for_log(value: str) -> str:
    """Return an ISO timestamp using a readable log-line format.

    The JSON fields keep the strict ISO value. Text logs keep ISO ordering but
    replace the machine separator to improve readability.
    """
    text = str(value).strip()
    if not text:
        return text

    formatted = text.replace("T", " ", 1)

    if formatted.endswith("Z"):
        return f"{formatted[:-1]} Z"

    if len(formatted) >= 6 and formatted[-6] in {"+", "-"} and formatted[-3] == ":":
        return f"{formatted[:-6]} {formatted[-6:]}"

    return formatted
