#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse NLP Complète - Comparaison des 3 Analyseurs
Tous les discours de Lee Seung Man (1021 discours)
Hannanum, Kkma, Komoran avec filtrage
"""

import json
import time
from collections import Counter
from konlpy.tag import Hannanum, Kkma, Komoran

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

def analyze_with_analyzer(analyzer_name, analyzer, speeches):
    """Analyse tous les discours avec un analyseur donné"""
    print(f"\n{'='*80}")
    print(f"🔍 ANALYSE AVEC {analyzer_name.upper()}")
    print(f"{'='*80}")
    
    start_time = time.time()
    all_nouns = []
    
    for idx, speech in enumerate(speeches, 1):
        if idx % 100 == 0:
            elapsed = time.time() - start_time
            print(f"  Progression: {idx}/{len(speeches)} discours ({elapsed:.1f}s)")
        
        # Combiner tous les paragraphes
        text = " ".join(speech["paragraphs"])
        
        # Extraire les noms
        nouns = analyzer.nouns(text)
        
        # Filtrer les stop words et mots courts
        nouns_filtered = [word for word in nouns if word not in KOREAN_STOPWORDS and len(word) > 1]
        
        all_nouns.extend(nouns_filtered)
    
    total_time = time.time() - start_time
    
    # Calculer les statistiques
    word_freq = Counter(all_nouns)
    top_50 = word_freq.most_common(50)
    
    print(f"\n✅ Analyse terminée en {total_time:.2f} secondes")
    print(f"   Vitesse: {len(speeches)/total_time:.1f} discours/seconde")
    print(f"   Total de noms extraits: {len(all_nouns):,}")
    print(f"   Noms uniques: {len(word_freq):,}")
    
    print(f"\n🏆 TOP 10 MOTS LES PLUS FRÉQUENTS:")
    for rank, (word, count) in enumerate(top_50[:10], 1):
        print(f"  {rank:2d}. {word:20s} : {count:6,d} fois")
    
    return {
        "analyzer": analyzer_name,
        "execution_time_seconds": round(total_time, 2),
        "speeches_per_second": round(len(speeches)/total_time, 2),
        "total_nouns_extracted": len(all_nouns),
        "unique_nouns": len(word_freq),
        "average_nouns_per_speech": round(len(all_nouns)/len(speeches), 1),
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

# Charger les discours
print("="*80)
print("📖 ANALYSE NLP COMPARATIVE - LEE SEUNG MAN (이승만)")
print("="*80)
print("\n📂 Chargement des discours...")
with open("president_texts_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

total_speeches = len(speeches)
print(f"   ✓ {total_speeches:,} discours chargés\n")

# Initialiser les analyseurs
print("🔧 Initialisation des analyseurs...")
hannanum = Hannanum()
kkma = Kkma()
komoran = Komoran()
print("   ✓ Tous les analyseurs prêts\n")

# Analyser avec chaque analyseur
all_results = []

# HANNANUM
result_hannanum = analyze_with_analyzer("Hannanum", hannanum, speeches)
all_results.append(result_hannanum)

# KKMA
result_kkma = analyze_with_analyzer("Kkma", kkma, speeches)
all_results.append(result_kkma)

# KOMORAN
result_komoran = analyze_with_analyzer("Komoran", komoran, speeches)
all_results.append(result_komoran)

# RÉSUMÉ COMPARATIF
print("\n" + "="*80)
print("📊 RÉSUMÉ COMPARATIF - TOUS LES ANALYSEURS")
print("="*80)
print(f"\n{'Analyseur':<15} {'Temps (s)':<12} {'Vitesse':<15} {'Noms extraits':<15} {'Noms uniques':<15}")
print("-" * 80)
for result in all_results:
    print(f"{result['analyzer']:<15} {result['execution_time_seconds']:<12.2f} "
          f"{result['speeches_per_second']:<15.1f} "
          f"{result['total_nouns_extracted']:<15,d} "
          f"{result['unique_nouns']:<15,d}")

# Comparaison des Top 10
print("\n" + "="*80)
print("🏆 COMPARAISON DES TOP 10 MOTS")
print("="*80)

for result in all_results:
    print(f"\n{result['analyzer']}:")
    for item in result['top_50_words'][:10]:
        print(f"  {item['rank']:2d}. {item['word']:20s} : {item['frequency']:6,d} fois")

# Sauvegarder les résultats
output = {
    "metadata": {
        "president": "Lee Seung Man (이승만)",
        "total_speeches": total_speeches,
        "stopwords_filtering": True,
        "stopwords_count": len(KOREAN_STOPWORDS),
        "analysis_date": "2025-12-09"
    },
    "results": all_results
}

output_file = "lee_seung_man_all_analyzers.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("💾 RÉSULTATS SAUVEGARDÉS")
print("="*80)
print(f"  Fichier: {output_file}")
print("\nContenu:")
print("  • Résultats des 3 analyseurs (Hannanum, Kkma, Komoran)")
print("  • Temps d'exécution pour chaque analyseur")
print("  • Top 50 mots pour chaque analyseur")
print("  • Statistiques comparatives")

print("\n" + "="*80)
print("✅ ANALYSE COMPARATIVE COMPLÈTE TERMINÉE")
print("="*80)
