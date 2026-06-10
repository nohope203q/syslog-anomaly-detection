---
name: syslog-anomaly-chain
description: >
  Chain chạy pipeline phát hiện bất thường syslog: ingest, embedding,
  song song Centroid/KNN, ensemble voting và DeepSeek explanation.
---

# Syslog Anomaly Ensemble Chain

## Chain Stages

1. `syslog-ingest`
   - Input: `data/input/<input_file>.log`
   - Output: `data/processed/<input_stem>_records.jsonl`

2. `embedding-builder`
   - Input: JSONL records từ stage ingest
   - Output: `data/embeddings/<input_stem>_embeddings.npy`

3. `parallel_scoring`
   - Nhánh A: `centroid-detector`
   - Nhánh B: `knn-detector`
   - Hai nhánh cùng đọc records + embeddings nhưng không phụ thuộc kết quả của
     nhau, nên được phép chạy song song.
   - Output:
     - `triage/<input_stem>_centroid_scores.json`
     - `triage/<input_stem>_knn_scores.json`

4. `ensemble-voter`
   - Input: hai file score từ stage song song
   - Output: `triage/<input_stem>_ensemble_anomalies.json`

5. `deepseek-explainer`
   - Input: top-k anomaly từ ensemble
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
