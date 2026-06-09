---
name: knn_detector
description: >
  Dùng khi cần phát hiện điểm dị thường (outliers) bằng thuật toán 
  K-Nearest Neighbors (KNN) cho tập dữ liệu syslog. 
  Kích hoạt khi: chạy mô hình KNN, đo khoảng cách KNN, 
  hoặc chạy bước detection thứ hai của pipeline.
---

# KNN Detector

Tính điểm dị thường dựa trên khoảng cách trung bình của một điểm dữ liệu tới K láng giềng gần nhất của nó. Những log đứng trơ trọi, không giống với các cụm log thông thường sẽ bị đánh giá là rủi ro.

## Setup

Không cần cài đặt thêm thư viện ngoài. Sử dụng Python 3 và thư viện `numpy`, `scikit-learn` đã có trong `requirements.txt`.

## Usage

```bash
python3 scripts/04_score_knn.py --records data/processed/ssh_records.jsonl --embeddings data/embeddings/ssh_embeddings.npy --k 5 --output triage/knn_scores.json
```

Chạy từ thư mục gốc của dự án. Hỗ trợ thay đổi số láng giềng qua tham số `--k` (mặc định là 5).

## Output

Sinh file JSON tại `triage/knn_scores.json`.
Mỗi phần tử là một object chứa các trường log gốc cộng thêm trường `knn_score` (float).

## Notes

- KNN rất nặng về tính toán (O(N^2) complexity). Do đó script đã được hardcode chỉ xử lý 100.000 dòng dữ liệu đầu tiên.
- Script sử dụng `algorithm='brute'` và `n_jobs=-1` để ép CPU chạy đa luồng, tối đa hóa hiệu suất phần cứng.