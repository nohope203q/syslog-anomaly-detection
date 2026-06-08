# Kỹ Năng Tạo Embedding

Mục đích: chuyển các record SSH syslog đã parse thành vector dense để phục vụ
chấm điểm bất thường.

## File Phụ Trách

- Input: `data/processed/ssh_records.jsonl`
- Script: `scripts/02_embed_syslog.py`
- Output: `data/embeddings/ssh_embeddings.npy`

## Phương Pháp Baseline

Embedding baseline chạy cục bộ và cho kết quả ổn định:

1. Đọc trường `text_for_embedding` từ từng dòng JSONL.
2. Tách nội dung log thành unigram và bigram.
3. Dùng stable feature hashing để đưa token vào số chiều cố định.
4. Chuẩn hóa L2 cho từng vector.
5. Ghi vector `float32` ra file `.npy` tương thích với NumPy.


## Lệnh Chạy

```bash
python3 scripts/02_embed_syslog.py
python3 scripts/02_embed_syslog.py --dimensions 64
python3 scripts/02_embed_syslog.py --max-records 1000
```
