import argparse
import json
import os
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

def score_centroid(records_path, embeddings_path, output_path, limit=None):
    print(f"[*] Đang chạy Centroid Detector" + (f" (giới hạn {limit} dòng)..." if limit else "..."))
    
    # Load và cắt lát (nếu có limit)
    embeddings = np.load(embeddings_path)
    if limit:
        embeddings = embeddings[:limit]
        
    with open(records_path, 'r', encoding='utf-8') as f:
        records = []
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            records.append(json.loads(line))

    # Xử lý tính toán
    centroid = np.mean(embeddings, axis=0).reshape(1, -1)
    distances = euclidean_distances(embeddings, centroid).flatten()
    
    for i, rec in enumerate(records):
        rec["centroid_score"] = float(distances[i])
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
        
    print(f"[+] Đã lưu {len(records)} kết quả vào: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--embeddings", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=None, help="Số lượng dòng tối đa cần xử lý")
    args = parser.parse_args()
    score_centroid(args.records, args.embeddings, args.output, args.limit)