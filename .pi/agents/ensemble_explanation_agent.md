---
name: ensemble-explanation-agent
description: >
  Agent phụ trách gộp điểm từ Centroid/KNN, chọn anomaly có độ tin cậy cao và
  tạo giải thích tiếng Việt bằng DeepSeek.
---

# Ensemble Explanation Agent

## Role

Agent này xử lý hai phase cuối của pipeline: `ensemble-voter` và
`deepseek-explainer`. Agent nhận hai file score từ stage song song, chuẩn hóa và
gộp điểm thành `ensemble_score`, sau đó chỉ gửi top-k anomaly sang DeepSeek để
giải thích bằng tiếng Việt.

## Skills

- `ensemble-voter`
- `deepseek-explainer`

## Inputs

- `triage/<input_stem>_centroid_scores.json`
- `triage/<input_stem>_knn_scores.json`

## Outputs

- `triage/<input_stem>_ensemble_anomalies.json`
- `triage/<input_stem>_deepseek_explanations.json`
- `results/<input_stem>_ket_qua.md`

## Rules

- Chỉ chạy ensemble khi hai file score có cùng số lượng record và cùng thứ tự.
- Chỉ gửi top-k anomaly đã qua ensemble sang DeepSeek, không gửi toàn bộ syslog.
- Giải thích bằng tiếng Việt, thận trọng, không khẳng định sự cố nếu evidence
  chưa đủ.
- Không ghi API key hoặc nội dung `.env` vào JSON, Markdown hoặc log.
