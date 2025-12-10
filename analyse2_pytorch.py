import json
import time
import psutil
import subprocess
import torch
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import csr_matrix

# PyTorch-based LDA implementation
class PyTorchLDA:
    def __init__(self, n_topics=5, n_iter=100, random_state=42):
        self.n_topics = n_topics
        self.n_iter = n_iter
        self.random_state = random_state
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def fit(self, X):
        """Fit LDA model using PyTorch on GPU"""
        # Convert sparse matrix to dense numpy array
        if hasattr(X, 'toarray'):
            X_dense = X.toarray()
        else:
            X_dense = X
            
        n_docs, n_words = X_dense.shape
        
        # Initialize topic-word and doc-topic distributions on GPU
        torch.manual_seed(self.random_state)
        self.components_ = torch.rand(self.n_topics, n_words, device=self.device)
        self.components_ = self.components_ / self.components_.sum(dim=1, keepdim=True)
        
        doc_topic = torch.rand(n_docs, self.n_topics, device=self.device)
        doc_topic = doc_topic / doc_topic.sum(dim=1, keepdim=True)
        
        # Convert data to PyTorch tensor on GPU
        X_tensor = torch.tensor(X_dense, dtype=torch.float32, device=self.device)
        
        # EM algorithm
        for iteration in range(self.n_iter):
            # E-step: Update doc-topic distributions
            topic_word_t = self.components_.t()
            doc_topic = X_tensor @ topic_word_t
            doc_topic = doc_topic / (doc_topic.sum(dim=1, keepdim=True) + 1e-10)
            
            # M-step: Update topic-word distributions
            self.components_ = doc_topic.t() @ X_tensor
            self.components_ = self.components_ / (self.components_.sum(dim=1, keepdim=True) + 1e-10)
            
            if iteration % 20 == 0:
                print(f"  Iteration {iteration}/{self.n_iter}")
        
        # Convert back to numpy for compatibility
        self.components_ = self.components_.cpu().numpy()
        self.doc_topic_ = doc_topic.cpu().numpy()
        
        return self
    
    def transform(self, X):
        """Transform documents to topic distributions"""
        return self.doc_topic_

# Start monitoring
start_time = time.time()
process = psutil.Process()

print("=== PyTorch GPU-based LDA Analysis ===\n")
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")

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

# LDA Analysis
print("Vectorizing text...")
vectorizer = CountVectorizer(max_features=2000, min_df=2, max_df=0.8)
doc_term_matrix = vectorizer.fit_transform(paragraphs)

print("Running PyTorch LDA on GPU...")
lda = PyTorchLDA(n_topics=5, n_iter=100, random_state=42)
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
tsv_filename = "lda_pytorch_results.tsv"
with open(tsv_filename, 'w', encoding='utf-8') as f:
    f.write("Metric\tValue\n")
    f.write(f"Method\tPyTorch_GPU\n")
    f.write(f"Nb_Discours\t{nb_speeches}\n")
    f.write(f"Nb_Presidents\t{nb_presidents}\n")
    f.write(f"Nb_Paragraphs\t{nb_paragraphs}\n")
    f.write(f"Nb_Topics\t5\n")
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
