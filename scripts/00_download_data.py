#!/usr/bin/env python3
"""Tải bộ dữ liệu OpenSSH (Loghub) và tách thành SSH1/SSH2/SSH3.log.

Dataset: Loghub - OpenSSH (655,146 dòng, ~70MB), https://github.com/logpai/loghub
Kết quả giống hệt các file từng được commit trong repo (tương đương `split -n l/3`).
"""
import argparse
import io
import tarfile
import urllib.request
from pathlib import Path

URL = "https://zenodo.org/records/8196385/files/SSH.tar.gz?download=1"
INPUT_DIR = Path("data/input")


def split_by_size(data: bytes, parts: int) -> list[bytes]:
    """Chia theo kích thước tại ranh giới dòng (giống GNU `split -n l/N`)."""
    chunks, start, size = [], 0, len(data)
    for i in range(1, parts + 1):
        if i == parts:
            end = size
        else:
            end = data.find(b"\n", (size * i) // parts - 1)
            end = size if end == -1 else end + 1
        chunks.append(data[start:end])
        start = end
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-split", action="store_true", help="Chỉ tải SSH.log, không tách")
    args = parser.parse_args()

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = INPUT_DIR / "SSH.log"
    if not target.exists():
        print(f"Đang tải {URL} ...")
        with urllib.request.urlopen(URL) as resp:
            archive = resp.read()
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            member = next(m for m in tar.getmembers() if m.name.endswith("SSH.log"))
            target.write_bytes(tar.extractfile(member).read())
        print(f"Đã lưu {target}")
    else:
        print(f"{target} đã tồn tại, bỏ qua bước tải.")

    if not args.no_split:
        data = target.read_bytes()
        for idx, chunk in enumerate(split_by_size(data, 3), start=1):
            out = INPUT_DIR / f"SSH{idx}.log"
            out.write_bytes(chunk)
            lines = chunk.count(b"\n")
            print(f"Đã tạo {out} ({lines:,} dòng)")


if __name__ == "__main__":
    main()
