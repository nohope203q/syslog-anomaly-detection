---
name: syslog-ingest
description: >
  Dùng khi cần nạp và chuẩn hóa syslog SSH từ file log thô bất kỳ sang JSONL.
  Kích hoạt khi có yêu cầu: parse syslog, chuẩn hóa log SSH, tạo JSONL record,
  trích xuất trường từ file SSH/syslog được nêu trong prompt, hoặc chạy bước
  ingest của pipeline.
---

# Nạp Syslog

Parse log SSH thô thành các record JSONL đã chuẩn hóa để phục vụ các bước
embedding, chấm điểm centroid, KNN và ensemble.

## Setup

Không cần cài đặt thêm. Sử dụng Python 3 và thư viện trong `requirements.txt`.

## Usage

```bash
python3 scripts/01_prepare_syslog.py
python3 scripts/01_prepare_syslog.py --input data/input/<input_file>.log --output data/processed/<input_stem>_records.jsonl
python3 scripts/01_prepare_syslog.py --max-records 1000
python3 scripts/01_prepare_syslog.py --year 2016
```

Chạy từ thư mục gốc của dự án. Có thể ghi đè đường dẫn mặc định bằng các tham số
`--input`, `--output`, `--year`, và `--max-records`.

## Input từ prompt

- Nếu prompt nêu rõ file input, luôn dùng đúng file đó cho `--input`. Không tự
  đổi về mặc định `data/input/SSH.log`.
- File input có thể là đường dẫn tuyệt đối hoặc tương đối, ví dụ
  `/path/to/SSH2.log`, `data/input/SSH3.log`, hoặc một file `.log` khác.
- Nếu prompt chỉ nêu tên file như `SSH2.log` hoặc một tên `.log` bất kỳ, trước
  tiên tìm trong `data/input/`; nếu không tồn tại thì dùng đường dẫn đúng như
  người dùng cung cấp.
- Khi xử lý nhiều file khác nhau, đặt output riêng theo tên file input để tránh
  ghi đè. Quy ước khuyến nghị:
  `data/processed/<input_stem>_records.jsonl`.
- Sau khi chạy xong, báo lại chính xác cặp input/output đã dùng để các skill sau
  dùng tiếp đúng file JSONL này.

## Output

Mặc định sinh file JSONL tại `data/processed/ssh_records.jsonl`. Khi prompt chỉ
định file input cụ thể, ưu tiên output riêng theo quy ước
`data/processed/<input_stem>_records.jsonl`.
Mỗi dòng là một record đã chuẩn hóa, bao gồm các trường như `record_id`,
`raw`, `parse_status`, `timestamp`, `host`, `process`, `pid`, `message`,
`event_type`, `severity`, `source_ip`, `all_ips`, `port`, `user`, `rhost`,
`repeat_count`, và `text_for_embedding`.

## Notes

- Mặc định script lấy năm hiện tại của máy để điền vào timestamp
- Chỉ dùng `--year` khi chắc chắn toàn bộ log thuộc một năm cụ thể
- Log không parse được vẫn phải được ghi ra với `parse_status="unparsed"`
- `--max-records` hữu ích khi muốn thử nhanh trên một tập nhỏ
