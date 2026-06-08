#!/usr/bin/env python3
"""Prepare parsed SSH syslog records for anomaly detection."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


DEFAULT_INPUT = Path("data/input/SSH.log")
DEFAULT_OUTPUT = Path("data/processed/ssh_records.jsonl")

SYSLOG_RE = re.compile(
    r"^(?P<month>[A-Z][a-z]{2})\s+"
    r"(?P<day>\d{1,2})\s+"
    r"(?P<clock>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+"
    r"(?P<process>[A-Za-z0-9_./-]+)(?:\[(?P<pid>\d+)\])?:\s*"
    r"(?P<message>.*)$"
)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PORT_RE = re.compile(r"\bport\s+(?P<port>\d+)\b", re.IGNORECASE)
INVALID_USER_RE = re.compile(r"\binvalid user\s+(?P<user>[A-Za-z0-9._@+-]+)", re.IGNORECASE)
AUTH_USER_RE = re.compile(
    r"\b(?:failed|accepted)\s+(?:password|publickey)\s+for\s+(?:invalid user\s+)?(?P<user>[A-Za-z0-9._@+-]+)",
    re.IGNORECASE,
)
USER_KV_RE = re.compile(r"\buser=(?P<user>[A-Za-z0-9._@+-]+)", re.IGNORECASE)
RHOST_RE = re.compile(r"\brhost=(?P<rhost>\S+)", re.IGNORECASE)
REPEAT_RE = re.compile(r"message repeated (?P<count>\d+) times", re.IGNORECASE)


def classify(message: str) -> tuple[str, str]:
    text = message.lower()
    if "possible break-in attempt" in text:
        return "reverse_dns_breakin_warning", "high"
    if "too many authentication failures" in text:
        return "too_many_auth_failures", "high"
    if "failed password" in text:
        return "failed_password", "medium"
    if "authentication failure" in text:
        return "authentication_failure", "medium"
    if "invalid user" in text:
        return "invalid_user", "medium"
    if "accepted password" in text or "accepted publickey" in text:
        return "accepted_login", "low"
    if "session opened" in text:
        return "session_opened", "low"
    if "session closed" in text:
        return "session_closed", "low"
    if "disconnect" in text or "connection closed" in text:
        return "disconnect", "low"
    if "message repeated" in text:
        return "repeated_message", "medium"
    return "other", "info"


def first_group(pattern: re.Pattern[str], text: str, group: str) -> str | None:
    match = pattern.search(text)
    return match.group(group) if match else None


def parse_timestamp(month: str, day: str, clock: str, year: int) -> str:
    parsed = datetime.strptime(f"{year} {month} {day} {clock}", "%Y %b %d %H:%M:%S")
    return parsed.isoformat(timespec="seconds")


def extract_user(message: str) -> str | None:
    return (
        first_group(INVALID_USER_RE, message, "user")
        or first_group(AUTH_USER_RE, message, "user")
        or first_group(USER_KV_RE, message, "user")
    )


def build_text(record: dict[str, Any]) -> str:
    return " ".join(
        [
            f"process={record.get('process') or 'unknown'}",
            f"event={record.get('event_type')}",
            f"severity={record.get('severity')}",
            f"user={record.get('user') or 'unknown'}",
            f"source_ip={record.get('source_ip') or 'unknown'}",
            record.get("message") or "",
        ]
    )


def parse_line(line: str, record_id: int, year: int) -> dict[str, Any]:
    raw = line.rstrip("\n")
    match = SYSLOG_RE.match(raw)
    if not match:
        record = {
            "record_id": record_id,
            "raw": raw,
            "parse_status": "unparsed",
            "timestamp": None,
            "host": None,
            "process": None,
            "pid": None,
            "message": raw,
            "event_type": "unparsed",
            "severity": "unknown",
            "source_ip": None,
            "all_ips": [],
            "port": None,
            "user": None,
            "rhost": None,
            "repeat_count": 1,
        }
        record["text_for_embedding"] = build_text(record)
        return record

    parts = match.groupdict()
    message = parts["message"]
    event_type, severity = classify(message)
    ips = IP_RE.findall(message)
    port = first_group(PORT_RE, message, "port")
    repeat_count = first_group(REPEAT_RE, message, "count")

    record = {
        "record_id": record_id,
        "raw": raw,
        "parse_status": "parsed",
        "timestamp": parse_timestamp(parts["month"], parts["day"], parts["clock"], year),
        "host": parts["host"],
        "process": parts["process"],
        "pid": int(parts["pid"]) if parts["pid"] else None,
        "message": message,
        "event_type": event_type,
        "severity": severity,
        "source_ip": ips[0] if ips else None,
        "all_ips": ips,
        "port": int(port) if port else None,
        "user": extract_user(message),
        "rhost": first_group(RHOST_RE, message, "rhost"),
        "repeat_count": int(repeat_count) if repeat_count else 1,
    }
    record["text_for_embedding"] = build_text(record)
    return record


def iter_input(path: Path, max_records: int | None) -> Iterable[str]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle):
            if max_records is not None and index >= max_records:
                break
            if line.strip():
                yield line


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse SSH syslog lines into JSONL records.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--year", type=int, default=datetime.now().year)
    parser.add_argument("--max-records", type=int, default=None)
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input syslog file not found: {args.input}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    parsed = 0
    with args.output.open("w", encoding="utf-8") as output:
        for total, line in enumerate(iter_input(args.input, args.max_records), start=1):
            record = parse_line(line, total, args.year)
            parsed += int(record["parse_status"] == "parsed")
            output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"records={total} parsed={parsed} output={args.output}")


if __name__ == "__main__":
    main()
