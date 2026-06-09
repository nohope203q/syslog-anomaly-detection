---
name: embedding_builder
description: >
  Dùng khi cần tạo embedding cho các record SSH syslog đã chuẩn hóa,
  chuyển văn bản log thành vector số để phục vụ phát hiện bất thường.
  Kích hoạt khi có yêu cầu: tạo embedding, sinh vector từ syslog,
  mã hóa log thành vector, hoặc chạy bước embedding của pipeline.
---

# Tạo Embedding

Sinh vector dense từ các record SSH syslog đã xử lý để dùng cho các bước
chấm điểm và phát hiện bất thường.

## Setup

Không cần cài đặt thêm. Sử dụng Python 3 và thư viện trong `requirements.txt`.

## Usage

```bash
python3 scripts/02_embed_syslog.py
python3 scripts/02_embed_syslog.py --dimensions 64
python3 scripts/02_embed_syslog.py --max-records 1000
```

Chạy từ thư mục gốc của dự án. Có thể ghi đè đường dẫn mặc định bằng các tham số
`--records`, `--output`, `--text-field`, `--dimensions`, và `--max-records`.

## Output

Sinh file NumPy `.npy` tại `data/embeddings/ssh_embeddings.npy`.
Mỗi phần tử là một vector `float32` đã chuẩn hóa L2, tương ứng với một record
trong `data/processed/ssh_records.jsonl`.

## Notes

- Dùng baseline feature hashing cục bộ, không cần gọi model bên ngoài
- Mặc định đọc trường `text_for_embedding` từ mỗi record JSONL
- `--dimensions` phải là số dương
- `--max-records` hữu ích khi muốn thử nhanh trên tập dữ liệu nhỏ
