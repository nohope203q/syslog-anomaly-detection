---
name: knn-detector
description: >
  Dùng khi cần phát hiện điểm dị thường (outliers) bằng thuật toán 
  K-Nearest Neighbors (KNN) cho tập dữ liệu syslog. 
  Kích hoạt khi có yêu cầu: chạy mô hình KNN, đo khoảng cách KNN, 
  hoặc chạy bước detection thứ hai của pipeline nhận input từ bước embedding.
---

# KNN Detector

Tính điểm dị thường dựa trên khoảng cách trung bình của một điểm dữ liệu tới K láng giềng gần nhất của nó. Những log đứng trơ trọi, biệt lập và không thuộc về các cụm log vận hành thông thường sẽ bị đánh dấu là rủi ro.

## Setup

Không cần cài đặt thêm thư viện ngoài. Sử dụng Python 3 và các thư viện `numpy`, `scikit-learn` đã có trong `requirements.txt`.

## Usage

```bash
python3 scripts/04_score_knn.py --records data/processed/ssh_records.jsonl --embeddings data/embeddings/ssh_embeddings.npy --k 5 --output triage/knn_scores.json
```
```bash
python3 scripts/04_score_knn.py --records data/processed/<input_stem>_records.jsonl --embeddings data/embeddings/<input_stem>_embeddings.npy --k 5 --output triage/<input_stem>_knn_scores.json --limit 50000
```

Chạy từ thư mục gốc của dự án. Hỗ trợ cấu hình số láng giềng qua tham số `--k` (mặc định là 5) và giới hạn dòng bằng `--limit`.

## Input từ prompt

- Sử dụng chung cặp file đầu vào `--records` và `--embeddings` tương tự như bước Centroid Detector (do `embedding_builder` cung cấp).
- Nếu prompt chỉ định giới hạn số dòng, hãy truyền giá trị đó vào tham số `--limit`. **Bắt buộc giá trị `--limit` ở bước này phải trùng khớp hoàn toàn với giá trị đã dùng ở bước `centroid_detector`.**
- Đặt tên output đồng bộ với file dữ liệu đầu vào. Quy ước khuyến nghị: `triage/<input_stem>_knn_scores.json`.
- Báo cáo lại đường dẫn file output sau khi hoàn thành để chuẩn bị cho bước gộp điểm.

## Output

Sinh file JSON tại `triage/<input_stem>_knn_scores.json`.
Mỗi phần tử trong mảng là một object chứa các trường log gốc, được bổ sung thêm trường `knn_score` (float).

## Notes

- Thuật toán KNN có độ phức tạp tính toán rất lớn O(N^2). Do đó, khi chạy với tập dữ liệu lớn, việc sử dụng tham số `--limit` (khuyến nghị mức 100k - 200k dòng) là bắt buộc để tránh tình trạng treo máy hoặc timeout.
- Script đã được tối ưu hóa bằng cách ép cấu hình `algorithm='brute'` và `n_jobs=-1` để tận dụng tối đa kiến trúc đa luồng của CPU.
