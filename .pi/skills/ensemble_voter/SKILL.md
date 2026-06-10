---
name: ensemble-voter
description: >
  Dùng khi cần kết hợp các điểm dị thường từ hai mô hình độc lập (Centroid và KNN) 
  để ra quyết định cuối cùng (Ensemble Voting) và lọc ra danh sách các log đáng ngờ nhất.
  Kích hoạt khi có yêu cầu: gộp điểm anomaly, chạy mô hình ensemble, hoặc chốt kết quả detection cho một file log cụ thể.
---

# Hội Đồng Phán Xử (Ensemble Voter)

Đồng bộ và chuẩn hóa điểm số từ hai thuật toán Centroid và KNN bằng phương pháp Min-Max Scaling (đưa về thang đo chuẩn từ 0 đến 1). Sau đó, tính điểm trung bình `ensemble_score` và áp bộ lọc nhằm trích xuất ra top 5% các dòng log có hành vi dị thường, nguy hiểm nhất.

## Setup

Sử dụng Python 3 và thư viện lõi `numpy`. Không yêu cầu cài đặt thêm các thư viện học máy cồng kềnh.

## Usage

```bash
python3 scripts/05_ensemble_vote.py --centroid triage/centroid_scores.json --knn triage/knn_scores.json --output triage/ensemble_anomalies.json --percentile 95
```
```bash
python3 scripts/05_ensemble_vote.py --centroid triage/<input_stem>_centroid_scores.json --knn triage/<input_stem>_knn_scores.json --output triage/<input_stem>_ensemble_anomalies.json --percentile 95
```

Chạy từ thư mục gốc của dự án. Nhận đầu vào thông qua hai tham số bắt buộc là `--centroid` và `--knn`. Có thể chỉnh ngưỡng lọc bằng `--percentile`, mặc định là `95`.

## Input từ prompt

- Luôn lấy chính xác hai file kết quả trung gian từ bước `centroid_detector` và `knn_detector` vừa thực hiện thành công để truyền vào làm tham số.
- Đảm bảo file kết quả cuối cùng giữ nguyên tiền tố để phân biệt giữa các luồng log khác nhau. Quy ước khuyến nghị: `triage/<input_stem>_ensemble_anomalies.json`.

## Output

Sinh file JSON tại `triage/<input_stem>_ensemble_anomalies.json`.
Đây là danh sách các log nghi vấn cao (mặc định nằm ở Percentile thứ 95 trở lên), được sắp xếp theo thứ tự nguy hiểm giảm dần. Mỗi phần tử chứa đầy đủ bộ 3 chỉ số: `centroid_score`, `knn_score`, và `ensemble_score`.

## Notes

- Yêu cầu tiên quyết: Số lượng phần tử trong hai file đầu vào (Centroid và KNN) phải khớp nhau hoàn toàn, không được lệch dòng.
- Đầu ra của file này sẽ là dữ liệu đầu vào trực tiếp cho tầng giải thích ngôn ngữ tự nhiên (Phase tiếp theo của hệ thống).
