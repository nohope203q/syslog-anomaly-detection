---
name: parallel-detector-agent
description: >
  Agent phụ trách stage chấm điểm bất thường song song bằng Centroid detector
  và KNN detector trên cùng bộ embeddings.
---

# Parallel Detector Agent

## Role

Agent này chạy phase scoring của pipeline. Sau khi embeddings đã sẵn sàng, hai
detector `centroid-detector` và `knn-detector` cùng đọc records + embeddings
nhưng không phụ thuộc output của nhau. Vì vậy hai nhánh này có thể chạy song
song để rút ngắn thời gian scoring.

## Skills

- `centroid-detector`
- `knn-detector`

## Inputs

- `data/processed/<input_stem>_records.jsonl`
- `data/embeddings/<input_stem>_embeddings.npy`

## Outputs

- `triage/<input_stem>_centroid_scores.json`
- `triage/<input_stem>_knn_scores.json`

## Parallelism

Centroid scoring và KNN scoring là hai tác vụ độc lập sau khi embedding đã được
tạo. Trong code, parallelism thật được thực hiện bởi `ThreadPoolExecutor` trong
`scripts/run_pipeline.py` khi bật tham số `--parallel`.

## Rules

- Centroid và KNN phải dùng cùng một cặp records/embeddings.
- Nếu có `--limit`, giá trị limit của Centroid và KNN phải giống nhau.
- Không chạy ensemble trước khi cả hai file score đều đã được tạo thành công.
