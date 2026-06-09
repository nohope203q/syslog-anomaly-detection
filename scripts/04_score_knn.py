import argparse
import json
import os
import numpy as np
from sklearn.neighbors import NearestNeighbors

def score_knn(records_path, embeddings_path, k, output_path):
    print(f"[*] Đang chạy KNN Detector (k={k}, giới hạn 100.000 dòng)...")
    embeddings = np.load(embeddings_path)[:100000]
    
    with open(records_path, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f][:100000]

    nbrs = NearestNeighbors(n_neighbors=k, algorithm='brute', n_jobs=-1).fit(embeddings)
    distances, _ = nbrs.kneighbors(embeddings)
    knn_scores = distances.mean(axis=1)

    for i, rec in enumerate(records):
        rec["knn_score"] = float(knn_scores[i])
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
        
    print(f"[+] Đã lưu kết quả KNN vào: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--embeddings", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    score_knn(args.records, args.embeddings, args.k, args.output)