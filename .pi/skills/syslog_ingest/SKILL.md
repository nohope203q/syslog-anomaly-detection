---
name: syslog_ingest
description: >
  Dùng khi cần nạp và chuẩn hóa syslog SSH từ file log thô sang JSONL.
  Kích hoạt khi có yêu cầu: parse syslog, chuẩn hóa log SSH, tạo JSONL record,
  trích xuất trường từ SSH.log, hoặc chạy bước ingest của pipeline.
---

# Nạp Syslog

Parse log SSH thô thành các record JSONL đã chuẩn hóa để phục vụ các bước
embedding, chấm điểm centroid, KNN và ensemble.

## Setup

Không cần cài đặt thêm. Sử dụng Python 3 và thư viện trong `requirements.txt`.

## Usage

```bash
python3 scripts/01_prepare_syslog.py
python3 scripts/01_prepare_syslog.py --max-records 1000
python3 scripts/01_prepare_syslog.py --year 2016
```

Chạy từ thư mục gốc của dự án. Có thể ghi đè đường dẫn mặc định bằng các tham số
`--input`, `--output`, `--year`, và `--max-records`.

## Output

Sinh file JSONL tại `data/processed/ssh_records.jsonl`.
Mỗi dòng là một record đã chuẩn hóa, bao gồm các trường như `record_id`,
`raw`, `parse_status`, `timestamp`, `host`, `process`, `pid`, `message`,
`event_type`, `severity`, `source_ip`, `all_ips`, `port`, `user`, `rhost`,
`repeat_count`, và `text_for_embedding`.

## Notes

- Mặc định script lấy năm hiện tại của máy để điền vào timestamp
- Chỉ dùng `--year` khi chắc chắn toàn bộ log thuộc một năm cụ thể
- Log không parse được vẫn phải được ghi ra với `parse_status="unparsed"`
- `--max-records` hữu ích khi muốn thử nhanh trên một tập nhỏ
