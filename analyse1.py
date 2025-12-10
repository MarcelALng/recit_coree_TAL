import json
import time
import psutil
import subprocess
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Start monitoring
start_time = time.time()
process = psutil.Process()

# Load speeches
with open("presidential_speeches_texts_cleaned.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

# Extract unique presidents
presidents = set()
for speech in speeches:
    if "president" in speech:
        presidents.add(speech["president"])
    elif "url" in speech:
        # Extract president name from URL if available
        url_parts = speech["url"].split("/")
        if len(url_parts) > 4:
            presidents.add(url_parts[4])

nb_speeches = len(speeches)
nb_presidents = len(presidents) if presidents else "Unknown"
paragraphs = [p for article in speeches for p in article["paragraphs"]]
nb_paragraphs = len(paragraphs)

print(f"Nombre de discours : {nb_speeches}")
print(f"Nombre de présidents : {nb_presidents}")
print(f"Nombre de paragraphes : {nb_paragraphs}")

# LDA Analysis
MY_RS = 42
vectorizer = CountVectorizer(max_features=2000, min_df=2, max_df=0.8)
doc_term_matrix = vectorizer.fit_transform(paragraphs)

lda = LatentDirichletAllocation(n_components=15, random_state=MY_RS)
lda.fit(doc_term_matrix)

# Get top words per topic
vocab = vectorizer.get_feature_names_out()
topics_data = []
print("\n=== LDA Topics ===")
for idx, topic in enumerate(lda.components_):
    top_words = [vocab[i] for i in topic.argsort()[-10:]]
    topic_str = ' | '.join(top_words)
    topics_data.append({
        'topic_id': idx + 1,
        'top_words': topic_str
    })
    print(f"Thème {idx+1} : {topic_str}")

# Get topic distributions
topic_distributions = lda.transform(doc_term_matrix)
dominant_topics = topic_distributions.argmax(axis=1)

# Count paragraphs per topic
topic_counts = {}
for topic_idx in dominant_topics:
    topic_counts[topic_idx] = topic_counts.get(topic_idx, 0) + 1

# End monitoring
end_time = time.time()
execution_time = end_time - start_time

# Get CPU and memory usage
cpu_percent = process.cpu_percent(interval=0.1)
memory_info = process.memory_info()
memory_percent = process.memory_percent()

# Try to get GPU usage
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
tsv_filename = "lda_analysis_15topics_results.tsv"
with open(tsv_filename, 'w', encoding='utf-8') as f:
    # Header
    f.write("Metric\tValue\n")
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
    
    # Topics
    f.write("Topic_ID\tNb_Paragraphs\tTop_Words\n")
    for topic_id, topic_info in enumerate(topics_data, 1):
        count = topic_counts.get(topic_id - 1, 0)
        f.write(f"{topic_id}\t{count}\t{topic_info['top_words']}\n")

print(f"\n✓ Résultats sauvegardés dans {tsv_filename}")
print(f"✓ Temps d'exécution : {execution_time:.2f}s")
print(f"✓ CPU : {cpu_percent:.1f}% | GPU : {gpu_usage:.1f}% | GPU Power : {gpu_power:.1f}W")