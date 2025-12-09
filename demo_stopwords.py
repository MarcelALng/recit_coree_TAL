#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Démonstration du filtrage des stop words en coréen
Comparaison avec et sans stop words sur les discours présidentiels
"""

import json
from konlpy.tag import Komoran
from collections import Counter

# Liste de stop words coréens couramment utilisés
KOREAN_STOPWORDS = {
    # Particules (조사)
    '이', '가', '을', '를', '은', '는', '에', '에서', '의', '와', '과', '로', '으로',
    '도', '만', '부터', '까지', '에게', '한테', '께', '보다', '처럼', '같이',
    
    # Pronoms (대명사)
    '나', '너', '저', '우리', '그', '이', '저', '여기', '거기', '저기',
    '이것', '그것', '저것', '누구', '무엇', '어디', '언제', '어떻게',
    
    # Verbes auxiliaires et terminaisons courantes
    '하다', '되다', '있다', '없다', '이다', '아니다',
    
    # Adverbes temporels/locatifs fréquents
    '지금', '오늘', '어제', '내일', '여기', '거기', '저기',
    
    # Conjonctions
    '그리고', '그러나', '하지만', '또', '또한', '및',
    
    # Nombres
    '일', '이', '삼', '사', '오', '육', '칠', '팔', '구', '십',
    
    # Autres mots fonctionnels
    '등', '것', '수', '때', '년', '월', '일'
}

# Charger les discours
print("📖 Chargement des discours de Lee Seung Man...")
with open("president_texts_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

# Prendre un échantillon (premier discours)
sample_speech = speeches[0]
sample_text = " ".join(sample_speech["paragraphs"][:2])  # 2 premiers paragraphes

print(f"   ✓ Texte échantillon: {len(sample_text)} caractères")
print(f"   Titre: {sample_speech['title']}\n")

# Analyser avec Komoran
print("🔍 Analyse morphologique avec Komoran...")
komoran = Komoran()
nouns = komoran.nouns(sample_text)

print(f"   ✓ {len(nouns)} noms extraits\n")

# Compter les fréquences SANS filtrage
print("=" * 80)
print("📊 TOP 20 NOMS LES PLUS FRÉQUENTS (SANS FILTRAGE)")
print("=" * 80)
noun_freq_no_filter = Counter(nouns)
for word, count in noun_freq_no_filter.most_common(20):
    print(f"  {word:15s} : {count:3d} fois")

# Filtrer les stop words
nouns_filtered = [word for word in nouns if word not in KOREAN_STOPWORDS and len(word) > 1]

print("\n" + "=" * 80)
print("📊 TOP 20 NOMS LES PLUS FRÉQUENTS (AVEC FILTRAGE)")
print("=" * 80)
noun_freq_filtered = Counter(nouns_filtered)
for word, count in noun_freq_filtered.most_common(20):
    print(f"  {word:15s} : {count:3d} fois")

# Statistiques
print("\n" + "=" * 80)
print("📈 STATISTIQUES")
print("=" * 80)
print(f"  Noms avant filtrage  : {len(nouns)}")
print(f"  Noms après filtrage  : {len(nouns_filtered)}")
print(f"  Mots filtrés         : {len(nouns) - len(nouns_filtered)} ({100*(len(nouns) - len(nouns_filtered))/len(nouns):.1f}%)")
print(f"  Noms uniques (avant) : {len(set(nouns))}")
print(f"  Noms uniques (après) : {len(set(nouns_filtered))}")

# Sauvegarder les résultats
results = {
    "sample_title": sample_speech['title'],
    "sample_length": len(sample_text),
    "total_nouns": len(nouns),
    "filtered_nouns": len(nouns_filtered),
    "stopwords_removed": len(nouns) - len(nouns_filtered),
    "top_20_no_filter": noun_freq_no_filter.most_common(20),
    "top_20_filtered": noun_freq_filtered.most_common(20),
    "stopwords_used": list(KOREAN_STOPWORDS)
}

with open("stopwords_analysis.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n💾 Résultats sauvegardés dans: stopwords_analysis.json")

# Exemples de stop words trouvés
stopwords_found = [word for word in nouns if word in KOREAN_STOPWORDS]
print(f"\n🚫 Exemples de stop words filtrés: {set(stopwords_found)}")
