---
name: syslog-anomaly-chain
description: >
  Chain chạy pipeline phát hiện bất thường syslog: ingest, embedding,
  song song Centroid/KNN, ensemble voting và DeepSeek explanation.
---

# Syslog Anomaly Ensemble Chain

## Chain Stages

1. `syslog-preprocess-agent`
   - Skills:
     - `syslog-ingest`
     - `embedding-builder`
   - Input: `data/input/<input_file>.log`
   - Output: `data/processed/<input_stem>_records.jsonl`
   - Output: `data/embeddings/<input_stem>_embeddings.npy`

2. `parallel-detector-agent`
   - Skills:
     - `centroid-detector`
     - `knn-detector`
   - Nhánh A: `centroid-detector`
   - Nhánh B: `knn-detector`
   - Hai nhánh cùng đọc records + embeddings nhưng không phụ thuộc kết quả của
     nhau, nên được phép chạy song song.
   - Output:
     - `triage/<input_stem>_centroid_scores.json`
     - `triage/<input_stem>_knn_scores.json`

3. `ensemble-explanation-agent`
   - Skills:
     - `ensemble-voter`
     - `deepseek-explainer`
   - Input: hai file score từ stage song song
   - Output: `triage/<input_stem>_ensemble_anomalies.json`
   - Output:
     - `triage/<input_stem>_deepseek_explanations.json`
     - `results/<input_stem>_ket_qua.md`

## Default Command

```bash
python3 scripts/run_pipeline.py --input data/input/SSH.log --top-k 10 --knn-k 5 --threshold-percentile 95 --parallel
```

## Evidence Rules

- Mọi phase phải ghi output ra đúng thư mục `data/`, `triage/`, `logs/` hoặc
  `results/`.
- Log audit chính là `logs/run_pipeline.log`.
- DeepSeek chỉ giải thích anomaly đã được ensemble chọn, không phân tích toàn bộ
  syslog thô.
