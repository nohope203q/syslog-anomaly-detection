#!/usr/bin/env python3
"""Build deterministic dense embeddings for SSH syslog JSONL records.

The implementation intentionally uses only the Python standard library so the
data layer can run before project dependencies are installed. It writes a valid
NumPy .npy file containing float32 vectors.
"""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import re
import struct
import sys
from pathlib import Path
from typing import Iterable


DEFAULT_RECORDS = Path("data/processed/ssh_records.jsonl")
DEFAULT_OUTPUT = Path("data/embeddings/ssh_embeddings.npy")
TOKEN_RE = re.compile(r"(?u)\b[\w.:@/-]+\b")


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    bigrams = [f"{left}_{right}" for left, right in zip(tokens, tokens[1:])]
    return tokens + bigrams


def stable_bucket(token: str, dimensions: int) -> tuple[int, float]:
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    value = int.from_bytes(digest, "little", signed=False)
    bucket = value % dimensions
    sign = 1.0 if ((value >> 63) & 1) == 0 else -1.0
    return bucket, sign


def embed_text(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        bucket, sign = stable_bucket(token, dimensions)
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]


def count_records(path: Path, max_records: int | None) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for count, line in enumerate(handle, start=1):
            if max_records is not None and count > max_records:
                return max_records
            if not line.strip():
                count -= 1
    return count


def iter_texts(path: Path, text_field: str, max_records: int | None) -> Iterable[str]:
    emitted = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if max_records is not None and emitted >= max_records:
                break
            if not line.strip():
                continue
            record = json.loads(line)
            emitted += 1
            yield str(record.get(text_field) or record.get("message") or record.get("raw") or "")


def npy_header(rows: int, columns: int) -> bytes:
    header = f"{{'descr': '<f4', 'fortran_order': False, 'shape': ({rows}, {columns}), }}"
    header_bytes = header.encode("latin1")
    padding = 16 - ((10 + len(header_bytes) + 1) % 16)
    return b"\x93NUMPY\x01\x00" + struct.pack("<H", len(header_bytes) + padding + 1) + header_bytes + (b" " * padding) + b"\n"


def write_npy(path: Path, rows: int, columns: int, vectors: Iterable[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as output:
        output.write(npy_header(rows, columns))
        for vector in vectors:
            row = array.array("f", vector)
            if sys.byteorder != "little":
                row.byteswap()
            row.tofile(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create hash embeddings for parsed SSH syslog records.")
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--text-field", default="text_for_embedding")
    parser.add_argument("--dimensions", type=int, default=64)
    parser.add_argument("--max-records", type=int, default=None)
    args = parser.parse_args()

    if args.dimensions < 1:
        raise ValueError("--dimensions must be positive")
    if not args.records.exists():
        raise FileNotFoundError(f"Parsed records not found: {args.records}")

    rows = count_records(args.records, args.max_records)
    if rows == 0:
        raise ValueError(f"No records found in {args.records}")

    vectors = (embed_text(text, args.dimensions) for text in iter_texts(args.records, args.text_field, args.max_records))
    write_npy(args.output, rows, args.dimensions, vectors)
    print(f"embeddings_shape=({rows}, {args.dimensions}) output={args.output}")


if __name__ == "__main__":
    main()
