---
name: centroid_detector
description: >
  Dùng khi cần chấm điểm bất thường (anomaly score) cho syslog bằng cách 
  đo khoảng cách từ log tới vector trung tâm (Centroid). 
  Kích hoạt khi: chạy thuật toán centroid, tìm log bất thường bằng centroid,
  hoặc chạy bước detection đầu tiên của pipeline.
---

# Chấm Điểm Centroid

Phát hiện bất thường bằng cách tính khoảng cách Euclidean từ mỗi vector log tới vector trung bình (Centroid) của toàn bộ tập dữ liệu. Khoảng cách càng xa, khả năng là log độc hại càng cao.

## Setup

Không cần cài đặt thêm thư viện ngoài. Sử dụng Python 3 và thư viện `numpy`, `scikit-learn` đã có trong `requirements.txt`.

## Usage

```bash
python3 scripts/03_score_centroid.py --records data/processed/ssh_records.jsonl --embeddings data/embeddings/ssh_embeddings.npy --output triage/centroid_scores.json
```

Chạy từ thư mục gốc của dự án. Có thể ghi đè đường dẫn bằng các tham số `--records`, `--embeddings`, và `--output`.

## Output

Sinh file JSON tại `triage/centroid_scores.json`.
Mỗi phần tử là một object chứa các trường log gốc cộng thêm trường `centroid_score` (float) thể hiện độ lệch so với mức bình thường.

## Notes

- Script đã được hardcode cắt giới hạn 100.000 dòng dữ liệu đầu tiên ngay lúc load file vào RAM để tránh tràn bộ nhớ và tối ưu thời gian chạy.
- Thuật toán đơn giản, chạy rất nhanh (O(N) complexity) so với KNN.