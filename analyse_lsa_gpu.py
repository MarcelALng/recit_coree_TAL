import json
import time
import psutil
import subprocess
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from googletrans import Translator

print("=== LSA + K-means Analysis (GPU) ===\n")
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB\n")

# Start monitoring
start_time = time.time()
process = psutil.Process()

# Load speeches
with open("presidential_speeches_texts_cleaned.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

# Extract unique presidents from URLs
presidents = set()
for speech in speeches:
    url = speech.get('url', '')
    if 'activePresident=' in url:
        pres = url.split('activePresident=')[1].split('&')[0]
        presidents.add(pres)

nb_speeches = len(speeches)
nb_presidents = len(presidents) if presidents else "Unknown"
paragraphs = [p for article in speeches for p in article["paragraphs"]]
nb_paragraphs = len(paragraphs)

print(f"Nombre de discours : {nb_speeches}")
print(f"Nombre de présidents : {nb_presidents}")
print(f"Nombre de paragraphes : {nb_paragraphs}\n")

# Vectorize with TF-IDF (CPU)
print("Vectorizing text with TF-IDF...")
vectorizer = TfidfVectorizer(max_features=2000, min_df=2, max_df=0.8)
tfidf_matrix = vectorizer.fit_transform(paragraphs)

# Convert to dense tensor and move to GPU
print("Moving data to GPU...")
tfidf_dense = torch.tensor(tfidf_matrix.toarray(), dtype=torch.float32).cuda()

# LSA using PyTorch SVD on GPU
print("Running LSA (SVD on GPU)...")
n_components = 15

# Perform SVD on GPU
U, S, Vt = torch.linalg.svd(tfidf_dense, full_matrices=False)

# Keep only top n_components
lsa_matrix = U[:, :n_components] @ torch.diag(S[:n_components])

# Normalize (add epsilon to avoid division by zero)
norms = torch.norm(lsa_matrix, dim=1, keepdim=True)
lsa_matrix = lsa_matrix / (norms + 1e-10)

# K-means clustering on GPU
print("Clustering with K-means on GPU...")
n_clusters = 15
max_iter = 300

# Initialize centroids randomly (simpler and more stable than k-means++)
torch.manual_seed(42)
indices = torch.randperm(lsa_matrix.shape[0], device=lsa_matrix.device)[:n_clusters]
centroids = lsa_matrix[indices].clone()

for iteration in range(max_iter):
    # Assign to nearest centroid
    distances = torch.cdist(lsa_matrix, centroids)
    clusters = distances.argmin(dim=1)
    
    # Update centroids
    new_centroids = torch.zeros_like(centroids)
    for k in range(n_clusters):
        mask = clusters == k
        if mask.sum() > 0:
            new_centroids[k] = lsa_matrix[mask].mean(dim=0)
        else:
            new_centroids[k] = centroids[k]
    
    # Check convergence
    if torch.allclose(centroids, new_centroids, atol=1e-4):
        print(f"  Converged at iteration {iteration}")
        break
    
    centroids = new_centroids
    
    if iteration % 50 == 0:
        print(f"  Iteration {iteration}/{max_iter}")

clusters = clusters.cpu().numpy()

# Get top words per cluster
vocab = vectorizer.get_feature_names_out()
topics_data = []

print("\n=== LSA Topics (via K-means clustering on GPU) ===")
for cluster_id in range(15):
    cluster_docs = [i for i, c in enumerate(clusters) if c == cluster_id]
    
    if len(cluster_docs) == 0:
        continue
    
    # Get average TF-IDF for this cluster
    cluster_tfidf = tfidf_matrix[cluster_docs].mean(axis=0).A1
    top_indices = cluster_tfidf.argsort()[-10:][::-1]
    top_words = [vocab[i] for i in top_indices]
    topic_str = ' | '.join(top_words)
    
    topics_data.append({
        'topic_id': cluster_id + 1,
        'top_words': topic_str,
        'nb_paragraphs': len(cluster_docs)
    })
    print(f"Thème {cluster_id+1} ({len(cluster_docs)} paragraphes) : {topic_str}")

# End monitoring
end_time = time.time()
execution_time = end_time - start_time

# Get CPU and memory usage
cpu_percent = process.cpu_percent(interval=0.1)
memory_percent = process.memory_percent()

# Get GPU usage
gpu_usage = 0
gpu_power = 0
try:
    result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,power.draw', 
                           '--format=csv,noheader,nounits'], 
                          capture_output=True, text=True, timeout=2)
    if result.returncode == 0:
        gpu_data = result.stdout.strip().split(',')
        gpu_usage = float(gpu_data[0].strip())
        gpu_power = float(gpu_data[1].strip())
except:
    pass

# Save results to TSV
tsv_filename = "lsa_gpu_15topics_results.tsv"
with open(tsv_filename, 'w', encoding='utf-8') as f:
    f.write("Metric\tValue\n")
    f.write(f"Method\tLSA_GPU_Kmeans\n")
    f.write(f"Nb_Discours\t{nb_speeches}\n")
    f.write(f"Nb_Presidents\t{nb_presidents}\n")
    f.write(f"Nb_Paragraphs\t{nb_paragraphs}\n")
    f.write(f"Nb_Topics\t15\n")
    f.write(f"Execution_Time_Sec\t{execution_time:.2f}\n")
    f.write(f"CPU_Usage_Percent\t{cpu_percent:.2f}\n")
    f.write(f"Memory_Usage_Percent\t{memory_percent:.2f}\n")
    f.write(f"GPU_Usage_Percent\t{gpu_usage:.2f}\n")
    f.write(f"GPU_Power_Watts\t{gpu_power:.2f}\n")
    f.write("\n")
    
    f.write("Topic_ID\tNb_Paragraphs\tTop_Words\n")
    for topic_info in topics_data:
        f.write(f"{topic_info['topic_id']}\t{topic_info['nb_paragraphs']}\t{topic_info['top_words']}\n")

print(f"\n✓ Résultats sauvegardés dans {tsv_filename}")

# Add translations
print("\nAjout des traductions françaises...")
translator = Translator()

def translate_korean_words(text):
    words = text.split(' | ')
    translated = []
    for word in words:
        try:
            translation = translator.translate(word, src='ko', dest='fr')
            translated.append(f"{word} ({translation.text})")
        except:
            translated.append(f"{word} (?)")
    return ' | '.join(translated)

with open(tsv_filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
in_topics = False
for line in lines:
    if line.strip().startswith('Topic_ID'):
        in_topics = True
        output_lines.append(line)
    elif in_topics and '\t' in line:
        parts = line.strip().split('\t')
        if len(parts) == 3:
            topic_id, nb_para, top_words = parts
            print(f"  Translating Topic {topic_id}...")
            translated = translate_korean_words(top_words)
            output_lines.append(f"{topic_id}\t{nb_para}\t{translated}\n")
        else:
            output_lines.append(line)
    else:
        output_lines.append(line)

tsv_translated = "lsa_gpu_15topics_results_translated.tsv"
with open(tsv_translated, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"✓ Traductions sauvegardées dans {tsv_translated}")
print(f"✓ Temps d'exécution : {execution_time:.2f}s")
print(f"✓ CPU : {cpu_percent:.1f}% | GPU : {gpu_usage:.1f}% | GPU Power : {gpu_power:.1f}W")
