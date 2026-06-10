---
name: embedding-builder
description: >
  Dùng khi cần tạo embedding cho các record SSH syslog đã chuẩn hóa từ đúng
  file input/pipeline đang được yêu cầu,
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
python3 scripts/02_embed_syslog.py --records data/processed/<input_stem>_records.jsonl --output data/embeddings/<input_stem>_embeddings.npy
python3 scripts/02_embed_syslog.py --dimensions 64
python3 scripts/02_embed_syslog.py --max-records 1000
```

Chạy từ thư mục gốc của dự án. Có thể ghi đè đường dẫn mặc định bằng các tham số
`--records`, `--output`, `--text-field`, `--dimensions`, và `--max-records`.

## Input từ prompt

- Nếu prompt yêu cầu xử lý một file log cụ thể, không dùng mặc định
  `data/processed/ssh_records.jsonl` trừ khi đó chính là output ingest vừa được
  tạo cho file input đó.
- Nếu bước `syslog_ingest` vừa chạy, luôn lấy đúng file JSONL mà bước đó báo ra
  và truyền vào `--records`.
- Nếu prompt chỉ nêu file log thô như `SSH2.log` hoặc một tên `.log` bất kỳ
  trong `data/input` nhưng chưa có JSONL tương ứng, cần chạy `syslog_ingest`
  trước với file đó, rồi dùng output JSONL của nó.
- Khi xử lý nhiều file khác nhau, đặt output embedding riêng theo tên file input
  hoặc tên records để tránh ghi đè. Quy ước khuyến nghị:
  `data/embeddings/<input_stem>_embeddings.npy`.
- Sau khi chạy xong, báo lại chính xác cặp records/output đã dùng để các bước
  centroid, KNN hoặc ensemble dùng tiếp đúng embedding này.

## Output

Mặc định sinh file NumPy `.npy` tại `data/embeddings/ssh_embeddings.npy`. Khi
prompt chỉ định file input cụ thể, ưu tiên output riêng theo quy ước
`data/embeddings/<input_stem>_embeddings.npy`.
Mỗi phần tử là một vector `float32` đã chuẩn hóa L2, tương ứng với một record
trong file JSONL truyền qua `--records`.

## Notes

- Dùng baseline feature hashing cục bộ, không cần gọi model bên ngoài
- Mặc định đọc trường `text_for_embedding` từ mỗi record JSONL
- `--dimensions` phải là số dương
- `--max-records` hữu ích khi muốn thử nhanh trên tập dữ liệu nhỏ
