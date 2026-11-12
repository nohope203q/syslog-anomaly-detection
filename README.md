# 🛡️ Syslog Anomaly Detection — SSH Log Ensemble Detector

Phát hiện hành vi bất thường trong log SSH (brute-force, dò user, reverse-mapping thất bại…) bằng **embedding + ensemble hai bộ phát hiện không giám sát (Centroid & KNN)**, sau đó dùng **LLM (DeepSeek/OpenAI)** để giải thích các log nghi vấn bằng ngôn ngữ tự nhiên.

> Đồ án môn Lập trình mạng — Nhóm 12, Topic 4.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)

---

## 🔄 Pipeline

```
data/input/*.log
   │  01_prepare_syslog.py   → parse log thô thành JSONL (timestamp, host, pid, event, IP, user…)
   ▼
data/processed/<stem>_records.jsonl
   │  02_embed_syslog.py     → vector hoá mỗi dòng log (hashing embedding, mặc định 64 chiều)
   ▼
data/embeddings/<stem>_embeddings.npy
   ├── 03_score_centroid.py  → khoảng cách tới tâm cụm        ┐ chạy song song
   └── 04_score_knn.py       → khoảng cách tới k láng giềng   ┘ (--parallel)
   ▼
   │  05_ensemble_vote.py    → chuẩn hoá min-max, lấy trung bình, lọc theo percentile (mặc định 95)
   ▼
triage/<stem>_ensemble_anomalies.json
   │  06_explain_anomalies.py → LLM giải thích top-K bất thường
   ▼
results/<stem>_ket_qua.md
```

`run_pipeline.py` chạy toàn bộ các bước trên và ghi thời gian từng bước vào `logs/run_pipeline.log`.

## 🚀 Bắt đầu nhanh

```bash
git clone https://github.com/nohope203q/syslog-anomaly-detection.git
cd syslog-anomaly-detection
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Chạy thử ngay với file mẫu 2.000 dòng có sẵn trong repo
python scripts/run_pipeline.py --input data/input/SSH_2k.log --parallel
```

Kết quả nằm ở `results/ssh_2k_ket_qua.md`.

### Chạy với bộ dữ liệu đầy đủ (655.146 dòng, ~70MB)

Dataset gốc quá lớn để lưu trên GitHub nên được tải riêng:

```bash
python scripts/00_download_data.py          # tải SSH.log và tách thành SSH1/SSH2/SSH3.log
python scripts/run_pipeline.py --parallel   # mặc định dùng data/input/SSH.log
python scripts/run_pipeline.py --input data/input/SSH2.log --parallel
```

### Giải thích bằng LLM (tuỳ chọn)

Tạo file `.env` ở thư mục gốc:

```env
DEEPSEEK_API_KEY=sk-...
# DEEPSEEK_MODEL=deepseek-chat
# hoặc dùng OpenAI: OPENAI_API_KEY=sk-...  (chạy với --provider openai)
```

Không có API key thì pipeline vẫn chạy, chỉ bỏ qua phần giải thích bằng LLM.

## ⚙️ Tham số chính của `run_pipeline.py`

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `--input` | `data/input/SSH.log` | File log đầu vào |
| `--parallel` | tắt | Chạy Centroid và KNN song song |
| `--knn-k` | `5` | Số láng giềng cho KNN |
| `--top-k` | `10` | Số bất thường gửi cho LLM giải thích |
| `--dimensions` | `64` | Số chiều embedding |
| `--max-records` / `--limit` | — | Giới hạn số dòng xử lý (để chạy thử nhanh) |
| `--provider` | `deepseek` | `deepseek` hoặc `openai` |

## 🤖 Cấu hình agent (`.pi/`)

Thư mục `.pi/` mô tả pipeline dưới dạng agent/skill/chain để chạy bằng AI coding agent:
`agents/` (preprocess, parallel detector, explanation), `skills/` (ingest, embedding, centroid, knn, ensemble, deepseek explainer), `chains/syslog_anomaly_chain.md` và `prompts/`.

## 📁 Cấu trúc thư mục

```
├── scripts/              # 00–06: các bước pipeline + run_pipeline.py
├── data/input/           # SSH_2k.log, SSH_attack_sample.log (dataset đầy đủ tải bằng script 00)
├── .pi/                  # cấu hình agent / skill / chain / prompt
└── requirements.txt
```

Các thư mục `data/processed`, `data/embeddings`, `triage`, `results`, `logs` được sinh ra khi chạy và không commit.

## 📚 Dữ liệu

Bộ log OpenSSH từ **Loghub** (Zhu et al., *Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics*, ISSRE 2023) — https://github.com/logpai/loghub
