#!/usr/bin/env python3
"""Explain top ensemble anomalies with DeepSeek/OpenAI-compatible API."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_INPUT = Path("triage/ensemble_anomalies.json")
DEFAULT_OUTPUT = Path("triage/deepseek_explanations.json")
DEFAULT_MARKDOWN = Path("results/ket_qua.md")


def load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Ensemble anomaly file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {path}")
    return data


def compact_anomaly(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record.get("record_id", record.get("id")),
        "timestamp": record.get("timestamp"),
        "host": record.get("host"),
        "process": record.get("process"),
        "event_type": record.get("event_type"),
        "severity": record.get("severity"),
        "source_ip": record.get("source_ip"),
        "user": record.get("user"),
        "message": record.get("message", record.get("raw")),
        "centroid_score": record.get("centroid_score"),
        "knn_score": record.get("knn_score"),
        "ensemble_score": record.get("ensemble_score"),
    }


def build_prompt(anomaly: dict[str, Any]) -> str:
    return (
        "Bạn là chuyên viên phân tích log bảo mật. Hãy giải thích bằng tiếng Việt "
        "rõ ràng, dễ hiểu vì sao dòng syslog dưới đây bị xem là bất thường. "
        "Chỉ được dựa trên JSON evidence được cung cấp, không bịa thêm IP, user, "
        "timestamp hoặc sự kiện khác. Không khẳng định chắc chắn có tấn công nếu "
        "bằng chứng chưa đủ; dùng cách diễn đạt thận trọng như 'có thể', "
        "'khả năng', 'cần kiểm tra thêm'.\n\n"
        "Trả về strict JSON với các field sau, giữ nguyên tên field tiếng Anh "
        "nhưng toàn bộ nội dung value phải là tiếng Việt:\n"
        "- record_id\n"
        "- short_reason: 1-2 câu nêu lý do bất thường chính\n"
        "- likely_cause: giải thích nguyên nhân khả dĩ dựa trên log và điểm số\n"
        "- severity: một trong các mức thấp, trung bình, cao\n"
        "- recommended_action: hành động kiểm tra/xử lý đề xuất\n\n"
        f"Input anomaly:\n{json.dumps(anomaly, ensure_ascii=False, indent=2)}"
    )


def parse_model_json(text: str, anomaly: dict[str, Any]) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            parsed.setdefault("record_id", anomaly.get("record_id"))
            return parsed
    except json.JSONDecodeError:
        pass
    return {
        "record_id": anomaly.get("record_id"),
        "short_reason": cleaned[:500],
        "likely_cause": "Model returned non-JSON text; manual review is needed.",
        "severity": anomaly.get("severity") or "unknown",
        "recommended_action": "Review the original log and detector scores.",
    }


def make_client(provider: str) -> tuple[OpenAI | None, str, str | None]:
    load_dotenv()
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("OPENAI_MODEL", "gpt-4o")

    if not api_key:
        return None, model, f"missing_{provider}_api_key"
    return OpenAI(api_key=api_key, base_url=base_url), model, None


def explain_with_model(
    anomalies: list[dict[str, Any]], provider: str, model_override: str | None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    client, env_model, setup_error = make_client(provider)
    model = model_override or env_model
    meta = {
        "provider": provider,
        "model": model,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "ok" if client else "skipped",
        "error": setup_error,
    }

    explanations: list[dict[str, Any]] = []
    for anomaly in anomalies:
        compact = compact_anomaly(anomaly)
        if client is None:
            explanations.append(
                {
                    "record_id": compact.get("record_id"),
                    "short_reason": "Bỏ qua bước giải thích vì chưa cấu hình API key.",
                    "likely_cause": "Cần chạy lại script sau khi cấu hình file .env của dự án.",
                    "severity": compact.get("severity") or "unknown",
                    "recommended_action": "Kiểm tra thủ công log gốc, điểm ensemble và các trường liên quan.",
                    "api_status": "skipped",
                }
            )
            continue

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Chỉ sử dụng JSON evidence được cung cấp. "
                        "Trả về strict JSON. Nội dung giải thích phải bằng tiếng Việt."
                    ),
                },
                {"role": "user", "content": build_prompt(compact)},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        item = parse_model_json(content, compact)
        item["api_status"] = "ok"
        explanations.append(item)

    return explanations, meta


def write_markdown(
    path: Path,
    source_path: Path,
    anomalies: list[dict[str, Any]],
    explanations: list[dict[str, Any]],
    meta: dict[str, Any],
) -> None:
    explanation_by_id = {item.get("record_id"): item for item in explanations}

    def cell(value: Any) -> str:
        return str(value or "").replace("|", "/").replace("\n", "<br>")

    lines = [
        "# Kết Quả Syslog Anomaly Ensemble Detector",
        "",
        f"- Input ensemble: `{source_path}`",
        f"- Provider: `{meta.get('provider')}`",
        f"- Model: `{meta.get('model')}`",
        f"- Generated at: `{meta.get('generated_at')}`",
        f"- Explanation status: `{meta.get('status')}`",
        "",
        "## Top Log Bất Thường",
        "",
        "| ID | Sự kiện | Source IP | Centroid | KNN | Ensemble | Lý do bất thường | Nguyên nhân khả dĩ | Khuyến nghị |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]

    for anomaly in anomalies:
        rid = anomaly.get("record_id", anomaly.get("id"))
        explanation = explanation_by_id.get(rid, {})
        lines.append(
            "| {rid} | {event} | {ip} | {centroid:.4f} | {knn:.4f} | {ensemble:.4f} | {reason} | {cause} | {action} |".format(
                rid=rid,
                event=str(anomaly.get("event_type") or "")[:40],
                ip=anomaly.get("source_ip") or "",
                centroid=float(anomaly.get("centroid_score") or 0.0),
                knn=float(anomaly.get("knn_score") or 0.0),
                ensemble=float(anomaly.get("ensemble_score") or 0.0),
                reason=cell(explanation.get("short_reason")),
                cause=cell(explanation.get("likely_cause")),
                action=cell(explanation.get("recommended_action")),
            )
        )

    lines.extend(["", "## Ghi Chú", ""])
    if meta.get("error"):
        lines.append(f"- Bước giải thích bằng API đã bị bỏ qua: `{meta['error']}`.")
    lines.append("- Điểm Centroid và KNN là evidence từ các phase trước của pipeline.")
    lines.append("- Giải thích của DeepSeek chỉ hỗ trợ phân tích, không phải kết luận sự cố đã được xác nhận.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Explain top ensemble anomalies.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--top-k", type=int, default=int(os.getenv("TOP_K_EXPLAIN", "10")))
    parser.add_argument("--provider", choices=["deepseek", "openai"], default="deepseek")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    anomalies = load_json(args.input)
    selected = anomalies[: max(args.top_k, 0)]
    explanations, meta = explain_with_model(selected, args.provider, args.model)

    payload = {"meta": meta, "source": str(args.input), "explanations": explanations}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.markdown, args.input, selected, explanations, meta)
    print(f"explained={len(explanations)} output={args.output} markdown={args.markdown}")


if __name__ == "__main__":
    main()
