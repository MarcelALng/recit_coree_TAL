#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse NLP Complète sur 100 Discours de Lee Seung Man
Compare 3 analyseurs (Hannanum, Kkma, Komoran) avec et sans filtrage stop words
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
    '등', '것', '수', '때', '년', '월', '일', '중', '간', '말', '점'
}

def analyze_with_analyzer(analyzer_name, analyzer, texts, use_stopwords=False):
    """Analyse les textes avec un analyseur donné"""
    print(f"\n{'='*80}")
    print(f"🔍 Analyse avec {analyzer_name} {'(AVEC filtrage)' if use_stopwords else '(SANS filtrage)'}")
    print(f"{'='*80}")
    
    start_time = time.time()
    all_nouns = []
    
    for idx, text in enumerate(texts, 1):
        if idx % 10 == 0:
            print(f"  Progression: {idx}/100 discours...")
        
        # Extraire les noms
        nouns = analyzer.nouns(text)
        
        # Filtrer si nécessaire
        if use_stopwords:
            nouns = [word for word in nouns if word not in KOREAN_STOPWORDS and len(word) > 1]
        
        all_nouns.extend(nouns)
    
    elapsed_time = time.time() - start_time
    
    # Calculer les fréquences
    word_freq = Counter(all_nouns)
    top_10 = word_freq.most_common(10)
    
    print(f"\n✓ Temps d'exécution: {elapsed_time:.2f} secondes")
    print(f"✓ Total de noms extraits: {len(all_nouns):,}")
    print(f"✓ Noms uniques: {len(word_freq):,}")
    print(f"\n📊 TOP 10 MOTS LES PLUS FRÉQUENTS:")
    for rank, (word, count) in enumerate(top_10, 1):
        print(f"  {rank:2d}. {word:20s} : {count:5,d} fois")
    
    return {
        "analyzer": analyzer_name,
        "with_stopwords_filter": use_stopwords,
        "execution_time_seconds": round(elapsed_time, 2),
        "total_nouns": len(all_nouns),
        "unique_nouns": len(word_freq),
        "top_10_words": [(word, count) for word, count in top_10]
    }

# Charger les discours
print("📖 Chargement des discours de Lee Seung Man...")
with open("president_texts_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

# Prendre les 100 premiers discours
speeches_100 = speeches[:100]
print(f"   ✓ {len(speeches_100)} discours chargés")

# Combiner tous les paragraphes de chaque discours
texts = []
for speech in speeches_100:
    combined_text = " ".join(speech["paragraphs"])
    texts.append(combined_text)

print(f"   ✓ Textes préparés pour l'analyse\n")

# Initialiser les analyseurs
print("🔧 Initialisation des analyseurs...")
hannanum = Hannanum()
kkma = Kkma()
komoran = Komoran()
print("   ✓ Analyseurs prêts\n")

# Stocker tous les résultats
all_results = []

# ========== HANNANUM ==========
print("\n" + "="*80)
print("HANNANUM - Analyse complète")
print("="*80)

result = analyze_with_analyzer("Hannanum", hannanum, texts, use_stopwords=False)
all_results.append(result)

result = analyze_with_analyzer("Hannanum", hannanum, texts, use_stopwords=True)
all_results.append(result)

# ========== KKMA ==========
print("\n" + "="*80)
print("KKMA - Analyse complète")
print("="*80)

result = analyze_with_analyzer("Kkma", kkma, texts, use_stopwords=False)
all_results.append(result)

result = analyze_with_analyzer("Kkma", kkma, texts, use_stopwords=True)
all_results.append(result)

# ========== KOMORAN ==========
print("\n" + "="*80)
print("KOMORAN - Analyse complète")
print("="*80)

result = analyze_with_analyzer("Komoran", komoran, texts, use_stopwords=False)
all_results.append(result)

result = analyze_with_analyzer("Komoran", komoran, texts, use_stopwords=True)
all_results.append(result)

# ========== RÉSUMÉ COMPARATIF ==========
print("\n" + "="*80)
print("📊 RÉSUMÉ COMPARATIF - TEMPS D'EXÉCUTION")
print("="*80)
print(f"\n{'Analyseur':<15} {'Filtrage':<15} {'Temps (sec)':<15} {'Noms extraits':<15}")
print("-" * 80)
for result in all_results:
    filtrage = "AVEC" if result["with_stopwords_filter"] else "SANS"
    print(f"{result['analyzer']:<15} {filtrage:<15} {result['execution_time_seconds']:<15.2f} {result['total_nouns']:<15,d}")

# Sauvegarder les résultats
output = {
    "metadata": {
        "total_speeches_analyzed": len(speeches_100),
        "stopwords_count": len(KOREAN_STOPWORDS),
        "analysis_date": "2025-12-09"
    },
    "results": all_results
}

with open("comprehensive_nlp_results.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("✅ ANALYSE TERMINÉE")
print("="*80)
print("\n💾 Résultats sauvegardés dans: comprehensive_nlp_results.json")
print("\nCe fichier contient:")
print("  • Temps d'exécution pour chaque analyseur")
print("  • Top 10 mots avec et sans filtrage")
print("  • Statistiques complètes")
