import json
import time
import psutil
import subprocess
from gensim import corpora
from gensim.models import LdaMulticore
from sklearn.feature_extraction.text import CountVectorizer

# Start monitoring
start_time = time.time()
process = psutil.Process()

print("=== Gensim LDA Analysis (Multicore) ===\n")

# Load speeches
with open("presidential_speeches_texts_cleaned.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

# Extract unique presidents
presidents = set()
for speech in speeches:
    if "president" in speech:
        presidents.add(speech["president"])
    elif "url" in speech:
        url_parts = speech["url"].split("/")
        if len(url_parts) > 4:
            presidents.add(url_parts[4])

nb_speeches = len(speeches)
nb_presidents = len(presidents) if presidents else "Unknown"
paragraphs = [p for article in speeches for p in article["paragraphs"]]
nb_paragraphs = len(paragraphs)

print(f"Nombre de discours : {nb_speeches}")
print(f"Nombre de présidents : {nb_presidents}")
print(f"Nombre de paragraphes : {nb_paragraphs}\n")

# Prepare data for Gensim
print("Tokenizing text...")
# Simple tokenization (split by whitespace)
texts = [p.split() for p in paragraphs]

# Create dictionary and corpus
print("Creating dictionary and corpus...")
dictionary = corpora.Dictionary(texts)

# Filter extremes (similar to min_df and max_df in sklearn)
dictionary.filter_extremes(no_below=2, no_above=0.8, keep_n=2000)

# Create bag-of-words corpus
corpus = [dictionary.doc2bow(text) for text in texts]

# LDA Analysis with multicore
print("Running Gensim LDA (multicore)...")
import multiprocessing
n_cores = multiprocessing.cpu_count()
print(f"Using {n_cores} CPU cores")

lda = LdaMulticore(
    corpus=corpus,
    id2word=dictionary,
    num_topics=5,
    random_state=42,
    passes=10,
    workers=n_cores,
    per_word_topics=True
)

# Get top words per topic
topics_data = []
print("\n=== LDA Topics ===")
for idx in range(5):
    topic_words = lda.show_topic(idx, topn=10)
    top_words = [word for word, _ in topic_words]
    topic_str = ' | '.join(top_words)
    topics_data.append({
        'topic_id': idx + 1,
        'top_words': topic_str
    })
    print(f"Thème {idx+1} : {topic_str}")

# Get topic distributions
print("\nCalculating topic distributions...")
dominant_topics = []
for doc in corpus:
    topic_dist = lda.get_document_topics(doc)
    if topic_dist:
        dominant_topic = max(topic_dist, key=lambda x: x[1])[0]
    else:
        dominant_topic = 0
    dominant_topics.append(dominant_topic)

# Count paragraphs per topic
topic_counts = {}
for topic_idx in dominant_topics:
    topic_counts[topic_idx] = topic_counts.get(topic_idx, 0) + 1

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
tsv_filename = "lda_gensim_results.tsv"
with open(tsv_filename, 'w', encoding='utf-8') as f:
    f.write("Metric\tValue\n")
    f.write(f"Method\tGensim_Multicore\n")
    f.write(f"Nb_Discours\t{nb_speeches}\n")
    f.write(f"Nb_Presidents\t{nb_presidents}\n")
    f.write(f"Nb_Paragraphs\t{nb_paragraphs}\n")
    f.write(f"Nb_Topics\t5\n")
    f.write(f"Nb_CPU_Cores\t{n_cores}\n")
    f.write(f"Execution_Time_Sec\t{execution_time:.2f}\n")
    f.write(f"CPU_Usage_Percent\t{cpu_percent:.2f}\n")
    f.write(f"Memory_Usage_Percent\t{memory_percent:.2f}\n")
    f.write(f"GPU_Usage_Percent\t{gpu_usage:.2f}\n")
    f.write(f"GPU_Power_Watts\t{gpu_power:.2f}\n")
    f.write("\n")
    
    f.write("Topic_ID\tNb_Paragraphs\tTop_Words\n")
    for topic_id, topic_info in enumerate(topics_data, 1):
        count = topic_counts.get(topic_id - 1, 0)
        f.write(f"{topic_id}\t{count}\t{topic_info['top_words']}\n")

print(f"\n✓ Résultats sauvegardés dans {tsv_filename}")
print(f"✓ Temps d'exécution : {execution_time:.2f}s")
print(f"✓ CPU : {cpu_percent:.1f}% | GPU : {gpu_usage:.1f}% | GPU Power : {gpu_power:.1f}W")
