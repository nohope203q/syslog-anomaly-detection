---
name: deepseek-explainer
description: >
  Dùng khi cần giải thích các syslog anomaly đã được Ensemble Voting chọn lọc
  bằng mô hình DeepSeek hoặc API tương thích OpenAI. Kích hoạt khi có yêu cầu:
  giải thích anomaly, tạo nhận xét bảo mật cho top anomaly, sinh file
  deepseek_explanations.json, hoặc hoàn tất bước giải thích cuối pipeline.
---

# DeepSeek Explainer

Giải thích ngắn gọn các log bất thường có độ tin cậy cao sau bước
`ensemble_voter`. Skill này không tự phát hiện anomaly mới, không đọc toàn bộ
syslog thô để suy đoán, và chỉ dựa trên dữ liệu đã được chọn trong
`triage/<input_stem>_ensemble_anomalies.json`.

Mục tiêu là biến kết quả chấm điểm thành nhận xét tiếng Việt dễ hiểu cho báo
cáo bảo mật: lý do log đáng ngờ, nguyên nhân có thể xảy ra, mức độ nghiêm trọng
và hành động khuyến nghị.

## Setup

Sử dụng Python 3 và các thư viện đã khai báo trong `requirements.txt`, đặc biệt
là `openai` và `python-dotenv`.

Sử dụng file `.env` đã có sẵn trong thư mục gốc của dự án để nạp cấu hình
DeepSeek. File này cần có các biến sau:

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
TOP_K_EXPLAIN=10
```

Không tạo mới hoặc ghi đè `.env` nếu file đã tồn tại. Không nộp file `.env`
thật trong ZIP; chỉ nộp `.env.example` nếu cần minh họa tên biến môi trường.

## Usage

```bash
python3 scripts/06_explain_anomalies.py --input triage/ensemble_anomalies.json --output triage/deepseek_explanations.json --markdown results/ket_qua.md --top-k 10 --provider deepseek
```

```bash
python3 scripts/06_explain_anomalies.py --input triage/<input_stem>_ensemble_anomalies.json --output triage/<input_stem>_deepseek_explanations.json --markdown results/<input_stem>_ket_qua.md --top-k 10 --provider deepseek
```

Chạy từ thư mục gốc của dự án. Đầu vào bắt buộc là file ensemble đã tạo ở bước
trước. Nếu script chưa hỗ trợ một tham số nào đó, giữ nguyên logic chính:
đọc ensemble JSON, chọn top-k anomaly, gọi DeepSeek, ghi JSON giải thích và ghi
Markdown tổng hợp.

## Input từ prompt

- Luôn dùng đúng file output mới nhất của `ensemble_voter`. Không tự ý dùng
  `triage/ensemble_anomalies.json` nếu pipeline đang xử lý một file log cụ thể
  như `SSH2.log` và đã có output dạng
  `triage/<input_stem>_ensemble_anomalies.json`.
- Chỉ gửi top-k anomaly cho DeepSeek. Mặc định dùng `TOP_K_EXPLAIN` trong `.env`
  hoặc `--top-k 10`; nếu prompt nêu số khác thì dùng đúng số đó.
- Yêu cầu DeepSeek trả nội dung giải thích bằng tiếng Việt rõ ràng, nhưng giữ
  nguyên tên field JSON để script xử lý ổn định.
- Không gửi toàn bộ syslog thô cho mô hình. Chỉ gửi các trường cần thiết từ
  ensemble JSON như `record_id`, `raw` hoặc `message`, `event_type`, `severity`,
  `source_ip`, `centroid_score`, `knn_score`, và `ensemble_score`.
- Nếu thiếu file ensemble, thiếu API key, hoặc JSON input không hợp lệ, dừng lại
  và báo rõ lỗi. Không tự tạo kết quả giả.
- Khi xử lý nhiều file log khác nhau, đặt output theo cùng tiền tố input:
  `triage/<input_stem>_deepseek_explanations.json` và
  `results/<input_stem>_ket_qua.md`.

## Output

Sinh file JSON tại `triage/<input_stem>_deepseek_explanations.json`. Mỗi phần tử
nên có các trường:

```json
{
  "record_id": 17,
  "short_reason": "Dòng log có dấu hiệu đăng nhập SSH thất bại bất thường từ IP bên ngoài.",
  "likely_cause": "Có thể là thử dò mật khẩu hoặc quét SSH tự động vào tài khoản không hợp lệ.",
  "severity": "cao",
  "recommended_action": "Kiểm tra thêm các lần đăng nhập từ IP này, đối chiếu auth log và cân nhắc chặn hoặc giới hạn truy cập."
}
```

Đồng thời ghi file Markdown tổng hợp tại `results/<input_stem>_ket_qua.md`,
bao gồm thông tin run, bảng top anomaly, điểm từ Centroid/KNN/Ensemble và phần
giải thích DeepSeek tương ứng.

## Notes

- Đây là phase cuối của pipeline, chạy sau `ensemble_voter`.
- DeepSeek chỉ đóng vai trò giải thích dựa trên evidence, không được xác nhận
  chắc chắn có tấn công nếu dữ liệu chưa đủ. Ưu tiên cách viết thận trọng như
  "có thể", "khả năng", "cần kiểm tra thêm".
- Không in API key, token hoặc nội dung `.env` ra terminal, JSON, Markdown hay
  log.
- Nếu không có mạng hoặc không có API key, có thể ghi trạng thái lỗi vào output
  thay vì bịa phần giải thích.
- Output của skill này là evidence quan trọng để đưa vào báo cáo `.docx` ở phần
  đánh giá kết quả và kết luận.
