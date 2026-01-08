#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse Textométrique Complète - Lee Seung Man
TF-IDF, LDA Topic Modeling, et Visualisations
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from konlpy.tag import Komoran
import numpy as np
import pandas as pd
from collections import Counter

# Configuration matplotlib pour le coréen
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Stop words
KOREAN_STOPWORDS = {
    '이', '가', '을', '를', '은', '는', '에', '에서', '의', '와', '과', '로', '으로',
    '도', '만', '부터', '까지', '에게', '한테', '께', '보다', '처럼', '같이',
    '나', '너', '저', '우리', '그', '이', '저', '여기', '거기', '저기',
    '이것', '그것', '저것', '누구', '무엇', '어디', '언제', '어떻게',
    '하다', '되다', '있다', '없다', '이다', '아니다',
    '지금', '오늘', '어제', '내일', '여기', '거기', '저기',
    '그리고', '그러나', '하지만', '또', '또한', '및',
    '일', '이', '삼', '사', '오', '육', '칠', '팔', '구', '십',
    '등', '것', '수', '때', '년', '월', '일', '중', '간', '말', '점', '바',
    '담화', '박사', '대통령이승만', '공보처', '공보실', '편', '집'
}

print("="*80)
print("📊 ANALYSE TEXTOMÉTRIQUE - LEE SEUNG MAN")
print("="*80)

# Charger les discours
print("\n📂 Chargement des discours...")
with open("president_texts_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

print(f"   ✓ {len(speeches)} discours chargés\n")

# Préparer les textes
print("🔧 Préparation des textes avec Komoran...")
komoran = Komoran()
documents = []
titles = []

for idx, speech in enumerate(speeches, 1):  # Tous les discours
    if idx % 100 == 0:
        print(f"   Traitement: {idx}/{len(speeches)} discours")
    
    text = " ".join(speech["paragraphs"])
    nouns = komoran.nouns(text)
    nouns_filtered = [w for w in nouns if w not in KOREAN_STOPWORDS 
                     and len(w) > 1 and not w.isdigit()]
    
    documents.append(" ".join(nouns_filtered))
    titles.append(speech["title"][:50])

print(f"   ✓ {len(documents)} documents préparés\n")

# ========== 1. TF-IDF ANALYSIS ==========
print("="*80)
print("📈 1. ANALYSE TF-IDF")
print("="*80)

tfidf_vectorizer = TfidfVectorizer(max_features=50, min_df=2)
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
feature_names = tfidf_vectorizer.get_feature_names_out()

# Top mots TF-IDF globaux
tfidf_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
top_indices = tfidf_scores.argsort()[-20:][::-1]

print("\n🏆 TOP 20 MOTS PAR TF-IDF (Importance globale):")
tfidf_results = []
for idx in top_indices:
    word = feature_names[idx]
    score = tfidf_scores[idx]
    print(f"  {word:15s} : {score:.4f}")
    tfidf_results.append({'word': word, 'tfidf_score': score})

# Visualisation TF-IDF avec traductions
print("\nGénération du graphique tfidf_analysis.png avec labels en français...")
from googletrans import Translator
translator = Translator()

words_ko = [feature_names[i] for i in top_indices[:15]]
scores = [tfidf_scores[i] for i in top_indices[:15]]

translated_labels = []
for word in words_ko:
    try:
        trans = translator.translate(word, src='ko', dest='fr').text
        clean_trans = trans.encode('ascii', 'ignore').decode('ascii').strip()
        if not clean_trans: clean_trans = "Terme"
        translated_labels.append(clean_trans)
    except:
        translated_labels.append("???")

plt.figure(figsize=(12, 6))
plt.barh(range(len(translated_labels)), scores)
plt.yticks(range(len(translated_labels)), translated_labels)
plt.xlabel('TF-IDF Score')
plt.title('Top 15 Mots par TF-IDF - Lee Seung Man (Traduit)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('tfidf_analysis.png', dpi=150, bbox_inches='tight')
print("💾 Graphique sauvegardé: tfidf_analysis.png")

# ========== 2. LDA TOPIC MODELING ==========
print("\n" + "="*80)
print("🎯 2. LDA TOPIC MODELING")
print("="*80)

n_topics = 5
print(f"\nNombre de topics: {n_topics}")

count_vectorizer = CountVectorizer(max_features=100, min_df=2)
count_matrix = count_vectorizer.fit_transform(documents)
count_features = count_vectorizer.get_feature_names_out()

lda_model = LatentDirichletAllocation(
    n_components=n_topics,
    random_state=42,
    max_iter=20,
    learning_method='online'
)

print("🔄 Entraînement du modèle LDA...")
lda_model.fit(count_matrix)

# Afficher les topics
print("\n📋 TOPICS IDENTIFIÉS:\n")
lda_topics = []
for topic_idx, topic in enumerate(lda_model.components_):
    top_indices = topic.argsort()[-10:][::-1]
    top_words = [count_features[i] for i in top_indices]
    top_scores = [topic[i] for i in top_indices]
    
    print(f"Topic {topic_idx + 1}:")
    print(f"  Mots clés: {', '.join(top_words[:7])}")
    
    lda_topics.append({
        'topic_id': topic_idx + 1,
        'top_words': top_words,
        'scores': [float(s) for s in top_scores]
    })

# Distribution des topics par document
doc_topic_dist = lda_model.transform(count_matrix)

# Visualisation des topics
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for topic_idx in range(n_topics):
    top_indices = lda_model.components_[topic_idx].argsort()[-10:][::-1]
    top_words = [count_features[i] for i in top_indices]
    top_scores = [lda_model.components_[topic_idx][i] for i in top_indices]
    
    axes[topic_idx].barh(range(len(top_words)), top_scores)
    axes[topic_idx].set_yticks(range(len(top_words)))
    axes[topic_idx].set_yticklabels(top_words)
    axes[topic_idx].set_xlabel('Importance')
    axes[topic_idx].set_title(f'Topic {topic_idx + 1}')
    axes[topic_idx].invert_yaxis()

# Supprimer le dernier subplot vide
fig.delaxes(axes[5])

plt.tight_layout()
plt.savefig('lda_topics_lee.png', dpi=150, bbox_inches='tight')
print("\n💾 Graphique sauvegardé: lda_topics_lee.png")

# ========== 3. LSA (Latent Semantic Analysis) ==========
print("\n" + "="*80)
print("🔬 3. LSA (LATENT SEMANTIC ANALYSIS)")
print("="*80)

n_components = 5
lsa_model = TruncatedSVD(n_components=n_components, random_state=42)

print(f"\nNombre de composantes: {n_components}")
print("🔄 Entraînement du modèle LSA...")

lsa_matrix = lsa_model.fit_transform(tfidf_matrix)

# Afficher les composantes
print("\n📋 COMPOSANTES SÉMANTIQUES:\n")
lsa_components = []
for idx, component in enumerate(lsa_model.components_):
    top_indices = np.abs(component).argsort()[-10:][::-1]
    top_words = [feature_names[i] for i in top_indices]
    top_scores = [component[i] for i in top_indices]
    
    print(f"Composante {idx + 1}:")
    print(f"  Concepts: {', '.join(top_words[:7])}")
    
    lsa_components.append({
        'component_id': idx + 1,
        'top_words': top_words,
        'scores': [float(s) for s in top_scores]
    })

# Variance expliquée
explained_variance = lsa_model.explained_variance_ratio_
print(f"\n📊 Variance expliquée: {explained_variance.sum():.2%}")

# Visualisation LSA
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for comp_idx in range(n_components):
    top_indices = np.abs(lsa_model.components_[comp_idx]).argsort()[-10:][::-1]
    top_words = [feature_names[i] for i in top_indices]
    top_scores = [lsa_model.components_[comp_idx][i] for i in top_indices]
    
    axes[comp_idx].barh(range(len(top_words)), top_scores)
    axes[comp_idx].set_yticks(range(len(top_words)))
    axes[comp_idx].set_yticklabels(top_words)
    axes[comp_idx].set_xlabel('Poids')
    axes[comp_idx].set_title(f'Composante LSA {comp_idx + 1}')
    axes[comp_idx].invert_yaxis()

fig.delaxes(axes[5])
plt.tight_layout()
plt.savefig('lsa_components_lee.png', dpi=150, bbox_inches='tight')
print("\n💾 Graphique sauvegardé: lsa_components_lee.png")

# ========== SAUVEGARDER LES RÉSULTATS ==========
results = {
    'president': 'Lee Seung Man (이승만)',
    'total_speeches_analyzed': len(documents),
    'tfidf_analysis': {
        'top_20_words': tfidf_results
    },
    'lda_topics': {
        'n_topics': n_topics,
        'topics': lda_topics
    },
    'lsa_analysis': {
        'n_components': n_components,
        'explained_variance': float(explained_variance.sum()),
        'components': lsa_components
    }
}

with open('textometry_Lee_Seung_Man.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("✅ ANALYSE TEXTOMÉTRIQUE TERMINÉE")
print("="*80)
print("\nFichiers créés:")
print("  📊 tfidf_analysis.png - Visualisation TF-IDF")
print("  🎯 lda_topics.png - Topics LDA")
print("  🔬 lsa_components.png - Composantes LSA")
print("  📁 textometry_Lee_Seung_Man.json - Résultats complets")
