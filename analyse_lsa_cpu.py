import json
import time
import psutil
import subprocess
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.preprocessing import Normalizer
from googletrans import Translator

# Start monitoring
start_time = time.time()
process = psutil.Process()

print("=== LSA + K-means Analysis (CPU) ===\n")

# Load speeches
with open("presidential_speeches_texts_cleaned_complete.json", "r", encoding="utf-8") as f:
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

# LSA Analysis with K-means clustering
print("Vectorizing text with TF-IDF...")
vectorizer = TfidfVectorizer(max_features=2000, min_df=2, max_df=0.8)
tfidf_matrix = vectorizer.fit_transform(paragraphs)

print("Running LSA (TruncatedSVD)...")
n_components = 15
svd = TruncatedSVD(n_components=n_components, random_state=42)
lsa_matrix = svd.fit_transform(tfidf_matrix)

# Normalize for better clustering
normalizer = Normalizer(copy=False)
lsa_matrix = normalizer.fit_transform(lsa_matrix)

print("Clustering with K-means...")
kmeans = KMeans(n_clusters=15, random_state=42, n_init=10, max_iter=300)
clusters = kmeans.fit_predict(lsa_matrix)

# Get top words per cluster by examining cluster centers
vocab = vectorizer.get_feature_names_out()
topics_data = []

print("\n=== LSA Topics (via K-means clustering) ===")
for cluster_id in range(15):
    # Get documents in this cluster
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

# Count paragraphs per cluster
topic_counts = {}
for cluster_id in clusters:
    topic_counts[cluster_id] = topic_counts.get(cluster_id, 0) + 1

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
tsv_filename = "lsa_cpu_15topics_results.tsv"
with open(tsv_filename, 'w', encoding='utf-8') as f:
    f.write("Metric\tValue\n")
    f.write(f"Method\tLSA_CPU_Kmeans\n")
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

tsv_translated = "lsa_cpu_15topics_results_translated.tsv"
with open(tsv_translated, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"✓ Traductions sauvegardées dans {tsv_translated}")
print(f"✓ Temps d'exécution : {execution_time:.2f}s")
print(f"✓ CPU : {cpu_percent:.1f}% | GPU : {gpu_usage:.1f}% | GPU Power : {gpu_power:.1f}W")
