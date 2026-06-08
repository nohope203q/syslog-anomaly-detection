# Kỹ Năng Nạp Syslog

Mục đích: parse file `data/input/SSH.log` thành các record chuẩn hóa để phục
vụ hệ thống Syslog Anomaly Ensemble Detector.

## File Phụ Trách

- Input: `data/input/SSH.log`
- Script: `scripts/01_prepare_syslog.py`
- Output: `data/processed/ssh_records.jsonl`

## Schema Record

Mỗi dòng JSONL cần có các trường:

- `record_id`
- `raw`
- `parse_status`
- `timestamp`
- `host`
- `process`
- `pid`
- `message`
- `event_type`
- `severity`
- `source_ip`
- `all_ips`
- `port`
- `user`
- `rhost`
- `repeat_count`
- `text_for_embedding`

## Lệnh Chạy

```bash
python3 scripts/01_prepare_syslog.py
python3 scripts/01_prepare_syslog.py --max-records 1000
```

Mặc định script sẽ tự lấy năm hiện tại của máy để gắn vào timestamp, vì syslog
RFC3164 không chứa thông tin năm. Chỉ dùng `--year` khi biết chắc log thuộc một
năm cụ thể:

```bash
python3 scripts/01_prepare_syslog.py --year 2016
```

Dòng log không nhận diện được vẫn phải được ghi ra với
`parse_status="unparsed"` thay vì làm dừng toàn bộ quá trình xử lý.
