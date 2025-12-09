#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse NLP Complète avec Komoran + Filtrage
Tous les discours de Lee Seung Man (1021 discours)
"""

import json
import time
from collections import Counter
from konlpy.tag import Komoran

# Liste de stop words coréens
KOREAN_STOPWORDS = {
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
    '등', '것', '수', '때', '년', '월', '일', '중', '간', '말', '점', '바'
}

print("="*80)
print("📖 ANALYSE NLP - LEE SEUNG MAN (이승만)")
print("="*80)
print("\n🔧 Configuration:")
print("  • Analyseur: Komoran")
print("  • Filtrage: AVEC stop words")
print("  • Fichier source: president_texts_Lee_Seung_Man.json\n")

# Charger les discours
print("📂 Chargement des discours...")
with open("president_texts_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

total_speeches = len(speeches)
print(f"   ✓ {total_speeches:,} discours chargés\n")

# Initialiser Komoran
print("🔧 Initialisation de Komoran...")
komoran = Komoran()
print("   ✓ Analyseur prêt\n")

# Analyser tous les discours
print("="*80)
print("🔍 ANALYSE EN COURS...")
print("="*80)

start_time = time.time()
all_nouns = []
speech_details = []

for idx, speech in enumerate(speeches, 1):
    # Afficher progression tous les 100 discours
    if idx % 100 == 0:
        elapsed = time.time() - start_time
        print(f"  Progression: {idx}/{total_speeches} discours ({elapsed:.1f}s)")
    
    # Combiner tous les paragraphes
    text = " ".join(speech["paragraphs"])
    
    # Extraire les noms
    nouns = komoran.nouns(text)
    
    # Filtrer les stop words et mots courts
    nouns_filtered = [word for word in nouns if word not in KOREAN_STOPWORDS and len(word) > 1]
    
    # Stocker les détails du discours
    speech_details.append({
        "title": speech["title"],
        "nouns_count": len(nouns_filtered),
        "unique_nouns": len(set(nouns_filtered)),
        "text_length": len(text)
    })
    
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
print(f"  Stop words filtrés        : {len(KOREAN_STOPWORDS)}")

print("\n" + "="*80)
print("🏆 TOP 50 MOTS LES PLUS FRÉQUENTS")
print("="*80)
for rank, (word, count) in enumerate(top_50, 1):
    print(f"  {rank:2d}. {word:20s} : {count:6,d} fois")

# Préparer les résultats pour JSON
results = {
    "metadata": {
        "president": "Lee Seung Man (이승만)",
        "analyzer": "Komoran",
        "stopwords_filtering": True,
        "total_speeches": total_speeches,
        "execution_time_seconds": round(total_time, 2),
        "speeches_per_second": round(total_speeches/total_time, 2),
        "analysis_date": "2025-12-09"
    },
    "statistics": {
        "total_nouns_extracted": len(all_nouns),
        "unique_nouns": len(word_freq),
        "average_nouns_per_speech": round(len(all_nouns)/total_speeches, 1),
        "stopwords_count": len(KOREAN_STOPWORDS)
    },
    "top_50_words": [
        {
            "rank": rank,
            "word": word,
            "frequency": count,
            "percentage": round(100 * count / len(all_nouns), 2)
        }
        for rank, (word, count) in enumerate(top_50, 1)
    ],
    "speech_details": speech_details[:10],  # Premiers 10 discours comme échantillon
    "stopwords_used": sorted(list(KOREAN_STOPWORDS))
}

# Sauvegarder les résultats
output_file = "lee_seung_man_nlp_analysis.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("💾 RÉSULTATS SAUVEGARDÉS")
print("="*80)
print(f"  Fichier: {output_file}")
print(f"  Taille: {len(json.dumps(results, ensure_ascii=False))/1024:.1f} KB")
print("\nContenu du fichier:")
print("  • Métadonnées (président, analyseur, temps)")
print("  • Statistiques globales")
print("  • Top 50 mots les plus fréquents")
print("  • Détails des 10 premiers discours (échantillon)")
print("  • Liste des stop words utilisés")

print("\n" + "="*80)
print("✅ ANALYSE COMPLÈTE TERMINÉE")
print("="*80)
