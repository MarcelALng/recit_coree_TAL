#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse Kkma SANS métadonnées
Filtre enrichi pour exclure les métadonnées des titres
"""

import json
import time
from collections import Counter
from konlpy.tag import Kkma

# Stop words coréens ENRICHIS (avec métadonnées)
KOREAN_STOPWORDS_ENRICHED = {
    # Particules
    '이', '가', '을', '를', '은', '는', '에', '에서', '의', '와', '과', '로', '으로',
    '도', '만', '부터', '까지', '에게', '한테', '께', '보다', '처럼', '같이',
    # Pronoms
    '나', '너', '저', '우리', '그', '이', '저', '여기', '거기', '저기',
    '이것', '그것', '저것', '누구', '무엇', '어디', '언제', '어떻게',
    # Verbes auxiliaires
    '하다', '되다', '있다', '없다', '이다', '아니다',
    # Adverbes temporels
    '지금', '오늘', '어제', '내일', '여기', '거기', '저기',
    # Conjonctions
    '그리고', '그러나', '하지만', '또', '또한', '및',
    # Nombres
    '일', '이', '삼', '사', '오', '육', '칠', '팔', '구', '십',
    # Autres mots fonctionnels
    '등', '것', '수', '때', '년', '월', '일', '중', '간', '말', '점', '바',
    
    # ========== MÉTADONNÉES À FILTRER ==========
    # Titres et sources
    '담화', '박사', '이승만', '대통령이승만', '대통령이승만박사',
    '대통령이승만박사담화', '대통령이승만박사담화집', '공보처', '공보실',
    '편', '집', '훈화록', '이대통령', '이대통령훈화록',
    # Années
    '1948', '1949', '1950', '1951', '1952', '1953', '1954', '1955',
    '1956', '1957', '1958', '1959', '1960',
    # Autres métadonnées courantes
    '중앙문화협회', '施政月報', '월보', '시정'
}

print("="*80)
print("📖 ANALYSE KKMA - SANS MÉTADONNÉES")
print("="*80)
print(f"\n🔧 Configuration:")
print(f"  • Analyseur: Kkma")
print(f"  • Filtrage: AVEC stop words enrichis")
print(f"  • Stop words totaux: {len(KOREAN_STOPWORDS_ENRICHED)}")
print(f"  • Fichier source: president_texts_Lee_Seung_Man.json\n")

# Charger les discours
print("📂 Chargement des discours...")
with open("president_texts_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

total_speeches = len(speeches)
print(f"   ✓ {total_speeches:,} discours chargés\n")

# Initialiser Kkma
print("🔧 Initialisation de Kkma...")
kkma = Kkma()
print("   ✓ Analyseur prêt\n")

# Analyser tous les discours
print("="*80)
print("🔍 ANALYSE EN COURS...")
print("="*80)

start_time = time.time()
all_nouns = []

for idx, speech in enumerate(speeches, 1):
    if idx % 100 == 0:
        elapsed = time.time() - start_time
        print(f"  Progression: {idx}/{total_speeches} discours ({elapsed:.1f}s)")
    
    # Combiner tous les paragraphes
    text = " ".join(speech["paragraphs"])
    
    # Extraire les noms
    nouns = kkma.nouns(text)
    
    # Filtrer les stop words ET métadonnées
    nouns_filtered = [
        word for word in nouns 
        if word not in KOREAN_STOPWORDS_ENRICHED 
        and len(word) > 1
        and not word.isdigit()  # Exclure les nombres purs
    ]
    
    all_nouns.extend(nouns_filtered)

total_time = time.time() - start_time

print(f"\n✅ Analyse terminée en {total_time:.2f} secondes")
print(f"   Vitesse: {total_speeches/total_time:.1f} discours/seconde\n")

# Calculer les statistiques
word_freq = Counter(all_nouns)
top_50 = word_freq.most_common(50)

print("="*80)
print("📊 STATISTIQUES GLOBALES")
print("="*80)
print(f"  Total de noms extraits    : {len(all_nouns):,}")
print(f"  Noms uniques              : {len(word_freq):,}")
print(f"  Moyenne par discours      : {len(all_nouns)/total_speeches:.1f} noms")
print(f"  Stop words filtrés        : {len(KOREAN_STOPWORDS_ENRICHED)}")

print("\n" + "="*80)
print("🏆 TOP 50 MOTS LES PLUS FRÉQUENTS (SANS MÉTADONNÉES)")
print("="*80)
for rank, (word, count) in enumerate(top_50, 1):
    print(f"  {rank:2d}. {word:20s} : {count:6,d} fois")

# Préparer les résultats
results = {
    "metadata": {
        "president": "Lee Seung Man (이승만)",
        "analyzer": "Kkma",
        "stopwords_filtering": True,
        "metadata_filtering": True,
        "total_speeches": total_speeches,
        "execution_time_seconds": round(total_time, 2),
        "speeches_per_second": round(total_speeches/total_time, 2),
        "analysis_date": "2025-12-09"
    },
    "statistics": {
        "total_nouns_extracted": len(all_nouns),
        "unique_nouns": len(word_freq),
        "average_nouns_per_speech": round(len(all_nouns)/total_speeches, 1),
        "stopwords_count": len(KOREAN_STOPWORDS_ENRICHED)
    },
    "top_50_words": [
        {
            "rank": rank,
            "word": word,
            "frequency": count,
            "percentage": round(100 * count / len(all_nouns), 2)
        }
        for rank, (word, count) in enumerate(top_50, 1)
    ]
}

# Sauvegarder
output_file = "kkma_no_metadata_analysis.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("💾 RÉSULTATS SAUVEGARDÉS")
print("="*80)
print(f"  Fichier: {output_file}")

print("\n" + "="*80)
print("✅ ANALYSE KKMA SANS MÉTADONNÉES TERMINÉE")
print("="*80)
