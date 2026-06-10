import argparse
import json
import os
import numpy as np

def ensemble_vote(centroid_path, knn_path, output_path, percentile=95.0):
    print("[*] Đang gộp điểm (Ensemble Voting)...")
    
    with open(centroid_path, 'r') as f: c_data = json.load(f)
    with open(knn_path, 'r') as f: k_data = json.load(f)

    c_scores = np.array([x["centroid_score"] for x in c_data])
    k_scores = np.array([x["knn_score"] for x in k_data])
    
    # Min-Max Scaling (0-1) để gộp cho chuẩn
    c_norm = (c_scores - c_scores.min()) / (c_scores.max() - c_scores.min() + 1e-9)
    k_norm = (k_scores - k_scores.min()) / (k_scores.max() - k_scores.min() + 1e-9)
    ensemble_scores = (c_norm + k_norm) / 2

    # Lấy nhóm nguy hiểm nhất theo ngưỡng percentile cấu hình.
    threshold = np.percentile(ensemble_scores, percentile)
    anomalies = []
    
    for i in range(len(c_data)):
        if ensemble_scores[i] >= threshold:
            rec = c_data[i].copy()
            rec["knn_score"] = float(k_scores[i])
            rec["ensemble_score"] = float(ensemble_scores[i])
            anomalies.append(rec)

    anomalies = sorted(anomalies, key=lambda x: x["ensemble_score"], reverse=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(anomalies, f, indent=2)

    print(f"[+] Phát hiện {len(anomalies)} log DỊ THƯỜNG ở percentile {percentile}. Lưu tại: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--centroid", required=True)
    parser.add_argument("--knn", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--percentile", type=float, default=95.0)
    args = parser.parse_args()
    ensemble_vote(args.centroid, args.knn, args.output, args.percentile)
