---
name: centroid-detector
description: >
  Dùng khi cần chấm điểm bất thường (anomaly score) cho syslog bằng cách 
  đo khoảng cách từ log tới vector trung tâm (Centroid). 
  Kích hoạt khi có yêu cầu: chạy thuật toán centroid, tìm log bất thường bằng centroid,
  hoặc chạy bước detection đầu tiên của pipeline nhận input từ bước embedding.
---

# Chấm Điểm Centroid

Phát hiện bất thường bằng cách tính khoảng cách Euclidean từ mỗi vector log tới vector trung bình (Centroid) của toàn bộ tập dữ liệu. Khoảng cách càng xa, khả năng là log độc hại hoặc hành vi tấn công càng cao.

## Setup

Không cần cài đặt thêm thư viện ngoài. Sử dụng Python 3 và các thư viện `numpy`, `scikit-learn` đã được khai báo trong `requirements.txt`.

## Usage

```bash
python3 scripts/03_score_centroid.py --records data/processed/ssh_records.jsonl --embeddings data/embeddings/ssh_embeddings.npy --output triage/centroid_scores.json
python3 scripts/03_score_centroid.py --records data/processed/<input_stem>_records.jsonl --embeddings data/embeddings/<input_stem>_embeddings.npy --output triage/<input_stem>_centroid_scores.json --limit 50000
```

Chạy từ thư mục gốc của dự án. Có thể ghi đè đường dẫn bằng các tham số `--records`, `--embeddings`, `--output`, và cấu hình giới hạn dòng bằng `--limit`.

## Input từ prompt

- Lấy chính xác cặp file `--records` và `--embeddings` mà bước `embedding_builder` vừa tạo ra để truyền vào. Không tự ý dùng file mặc định nếu prompt đang xử lý một luồng log cụ thể.
- Nếu prompt có yêu cầu giới hạn số lượng dòng chạy thử (ví dụ: "chạy 20k dòng", "quét 50000 dòng đầu"), hãy tự động trích xuất số đó và truyền vào tham số `--limit`.
- Đặt tên output đồng bộ với tên file dữ liệu đầu vào. Quy ước khuyến nghị: `triage/<input_stem>_centroid_scores.json`.
- Sau khi chạy xong, báo lại chính xác file output đã tạo để bước Ensemble kế tiếp sử dụng đúng nguồn dữ liệu.

## Output

Sinh file JSON tại `triage/<input_stem>_centroid_scores.json`.
Mỗi phần tử trong mảng là một object chứa toàn bộ các trường log gốc, được bổ sung thêm trường `centroid_score` (float) thể hiện độ lệch khoảng cách so với mức bình thường.

## Notes

- Thuật toán tính tiến trình tuyến tính O(N), thời gian xử lý cực nhanh và tiêu tốn ít tài nguyên phần cứng.
- Tham số `--limit` hỗ trợ cắt lát dữ liệu trực tiếp trên RAM, giúp tối ưu hiệu suất khi test nhanh hệ thống.
