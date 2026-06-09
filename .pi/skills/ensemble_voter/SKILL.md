---
name: ensemble_voter
description: >
  Dùng khi cần kết hợp các điểm dị thường từ hai model độc lập (Centroid và KNN) 
  để ra quyết định cuối cùng (Ensemble Voting) và lọc ra top các log đáng ngờ nhất.
  Kích hoạt khi: gộp điểm anomaly, chạy ensemble, hoặc chốt kết quả detection.
---

# Hội Đồng Phán Xử (Ensemble Voter)

Gộp điểm từ mô hình Centroid và KNN (sử dụng Min-Max Scaling đưa về thang 0-1) để tính điểm trung bình `ensemble_score`. Cuối cùng, lọc ra top 5% các dòng log có điểm dị thường cao nhất làm kết quả nghi vấn.

## Setup

Không cần cài thêm thư viện ML nặng, chỉ cần Python 3 và `numpy`.

## Usage

```bash
python3 scripts/05_ensemble_vote.py --centroid triage/centroid_scores.json --knn triage/knn_scores.json --output triage/ensemble_anomalies.json
```

## Output

Sinh file JSON tại `triage/ensemble_anomalies.json`.
Danh sách các log được sắp xếp từ mức độ nguy hiểm giảm dần. Mỗi record chứa đủ cả 3 loại điểm: `centroid_score`, `knn_score` và `ensemble_score`.

## Notes

- Yêu cầu tiên quyết: Số lượng record trong file đầu ra của Centroid và KNN phải khớp nhau hoàn toàn (đã được đồng bộ ở mức 100.000 dòng).
- Chỉ lấy các giá trị nằm trên Percentile thứ 95 (Top 5% nguy hiểm).