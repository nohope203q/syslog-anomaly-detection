import argparse
import json
import os
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

def score_centroid(records_path, embeddings_path, output_path):
    print(f"[*] Đang chạy Centroid Detector (giới hạn 100.000 dòng)...")
    embeddings = np.load(embeddings_path)[:100000] 
    
    with open(records_path, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f][:100000]

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
    args = parser.parse_args()
    score_centroid(args.records, args.embeddings, args.output)