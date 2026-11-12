#!/usr/bin/env python3
"""Run the full Syslog Anomaly Ensemble Detector pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path


DEFAULT_INPUT = Path("data/input/SSH.log")
DEFAULT_LOG = Path("logs/run_pipeline.log")


def log_line(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {message}\n")


def run_step(command: list[str], log_path: Path) -> float:
    started = time.perf_counter()
    log_line(log_path, "RUN " + " ".join(command))
    result = subprocess.run(command, text=True, capture_output=True)
    elapsed = time.perf_counter() - started
    if result.stdout:
        log_line(log_path, "STDOUT " + result.stdout.strip().replace("\n", " | "))
    if result.stderr:
        log_line(log_path, "STDERR " + result.stderr.strip().replace("\n", " | "))
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")
    log_line(log_path, f"DONE elapsed_seconds={elapsed:.3f}")
    return elapsed


def stem_for(path: Path) -> str:
    return path.stem.lower().replace(" ", "_")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run syslog anomaly detection pipeline.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--knn-k", type=int, default=5)
    parser.add_argument("--threshold-percentile", type=float, default=95.0, help="Documented threshold used by ensemble script.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--dimensions", type=int, default=64)
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--provider", choices=["deepseek", "openai"], default="deepseek")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--write-markdown", type=Path, default=None)
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input syslog file not found: {args.input}")

    stem = stem_for(args.input)
    records = Path(f"data/processed/{stem}_records.jsonl")
    embeddings = Path(f"data/embeddings/{stem}_embeddings.npy")
    centroid = Path(f"triage/{stem}_centroid_scores.json")
    knn = Path(f"triage/{stem}_knn_scores.json")
    ensemble = Path(f"triage/{stem}_ensemble_anomalies.json")
    explanations = Path(f"triage/{stem}_deepseek_explanations.json")
    markdown = args.write_markdown or Path(f"results/{stem}_ket_qua.md")

    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text("", encoding="utf-8")
    log_line(args.log, f"START input={args.input} parallel={args.parallel}")

    py = sys.executable
    timings: dict[str, float] = {}

    ingest_cmd = [py, "scripts/01_prepare_syslog.py", "--input", str(args.input), "--output", str(records)]
    if args.max_records is not None:
        ingest_cmd += ["--max-records", str(args.max_records)]
    timings["ingest"] = run_step(ingest_cmd, args.log)

    embed_cmd = [
        py,
        "scripts/02_embed_syslog.py",
        "--records",
        str(records),
        "--output",
        str(embeddings),
        "--dimensions",
        str(args.dimensions),
    ]
    if args.max_records is not None:
        embed_cmd += ["--max-records", str(args.max_records)]
    timings["embedding"] = run_step(embed_cmd, args.log)

    centroid_cmd = [
        py,
        "scripts/03_score_centroid.py",
        "--records",
        str(records),
        "--embeddings",
        str(embeddings),
        "--output",
        str(centroid),
    ]
    knn_cmd = [
        py,
        "scripts/04_score_knn.py",
        "--records",
        str(records),
        "--embeddings",
        str(embeddings),
        "--k",
        str(args.knn_k),
        "--output",
        str(knn),
    ]
    if args.limit is not None:
        centroid_cmd += ["--limit", str(args.limit)]
        knn_cmd += ["--limit", str(args.limit)]

    if args.parallel:
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as executor:
            centroid_future = executor.submit(run_step, centroid_cmd, args.log)
            knn_future = executor.submit(run_step, knn_cmd, args.log)
            timings["centroid"] = centroid_future.result()
            timings["knn"] = knn_future.result()
        timings["parallel_scoring_wall"] = time.perf_counter() - started
    else:
        timings["centroid"] = run_step(centroid_cmd, args.log)
        timings["knn"] = run_step(knn_cmd, args.log)

    timings["ensemble"] = run_step(
        [
            py,
            "scripts/05_ensemble_vote.py",
            "--centroid",
            str(centroid),
            "--knn",
            str(knn),
            "--output",
            str(ensemble),
            "--percentile",
            str(args.threshold_percentile),
        ],
        args.log,
    )

    timings["explain"] = run_step(
        [
            py,
            "scripts/06_explain_anomalies.py",
            "--input",
            str(ensemble),
            "--output",
            str(explanations),
            "--markdown",
            str(markdown),
            "--top-k",
            str(args.top_k),
            "--provider",
            args.provider,
        ],
        args.log,
    )

    for name, elapsed in timings.items():
        log_line(args.log, f"TIMING {name}={elapsed:.3f}s")
    log_line(args.log, f"FINISH markdown={markdown}")

    print(f"records={records}")
    print(f"embeddings={embeddings}")
    print(f"centroid={centroid}")
    print(f"knn={knn}")
    print(f"ensemble={ensemble}")
    print(f"explanations={explanations}")
    print(f"markdown={markdown}")
    print(f"log={args.log}")


if __name__ == "__main__":
    main()
