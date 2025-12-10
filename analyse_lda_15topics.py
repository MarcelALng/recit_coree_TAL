import json
import time
import psutil
import subprocess
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from googletrans import Translator

# Start monitoring
start_time = time.time()
process = psutil.Process()

print("=== LDA Topic Modeling Analysis ===\n")

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
nb_presidents = len(presidents)
paragraphs = [p for article in speeches for p in article["paragraphs"]]
nb_paragraphs = len(paragraphs)

print(f"Nombre de discours : {nb_speeches}")
print(f"Nombre de présidents : {nb_presidents}")
print(f"Présidents : {', '.join(sorted(presidents))}")
print(f"Nombre de paragraphes : {nb_paragraphs}\n")

# Vectorize with CountVectorizer for LDA
print("Vectorizing text with CountVectorizer...")
vectorizer = CountVectorizer(max_features=2000, min_df=2, max_df=0.8)
doc_term_matrix = vectorizer.fit_transform(paragraphs)

# LDA Topic Modeling
print("Running LDA Topic Modeling...")
n_topics = 15
lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=20, n_jobs=-1)
lda.fit(doc_term_matrix)

# Get top words per topic
vocab = vectorizer.get_feature_names_out()
topics_data = []

print("\n=== LDA Topics ===")
for topic_idx, topic in enumerate(lda.components_):
    top_indices = topic.argsort()[-10:][::-1]
    top_words = [vocab[i] for i in top_indices]
    topic_str = ' | '.join(top_words)
    
    # Get document distribution for this topic
    doc_topic_dist = lda.transform(doc_term_matrix)
    topic_docs = (doc_topic_dist[:, topic_idx] > 0.1).sum()
    
    topics_data.append({
        'topic_id': topic_idx + 1,
        'top_words': topic_str,
        'nb_paragraphs': int(topic_docs)
    })
    print(f"Thème {topic_idx+1} ({topic_docs} paragraphes) : {topic_str}")

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
tsv_filename = "lda_15topics_results.tsv"
with open(tsv_filename, 'w', encoding='utf-8') as f:
    f.write("Metric\tValue\n")
    f.write(f"Method\tLDA\n")
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

tsv_translated = "lda_15topics_results_translated.tsv"
with open(tsv_translated, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"✓ Traductions sauvegardées dans {tsv_translated}")
print(f"✓ Temps d'exécution : {execution_time:.2f}s")
print(f"✓ CPU : {cpu_percent:.1f}% | GPU : {gpu_usage:.1f}% | GPU Power : {gpu_power:.1f}W")
