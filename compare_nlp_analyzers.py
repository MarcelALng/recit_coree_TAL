#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comparaison des analyseurs morphologiques coréens (KoNLPy)
Teste Hannanum, Kkma et Komoran sur les discours de Lee Seung Man
"""

import json
import time
from konlpy.tag import Hannanum, Kkma, Komoran

# Charger les textes présidentiels
print("📖 Chargement des discours de Lee Seung Man...")
with open("president_texts_Lee_Seung_Man.json", "r", encoding="utf-8") as f:
    speeches = json.load(f)

print(f"   ✓ {len(speeches)} discours chargés\n")

# Prendre un échantillon de texte (premier discours, premiers 500 caractères)
sample_speech = speeches[0]
sample_text = " ".join(sample_speech["paragraphs"][:3])[:500]  # Premiers 500 caractères

print("📝 Texte d'exemple (500 caractères):")
print(f"   Titre: {sample_speech['title']}")
print(f"   Texte: {sample_text[:100]}...\n")
print("="*80)

# ========== HANNANUM ==========
print("\n🔍 Test 1/3: Hannanum")
print("-" * 80)
try:
    hannanum = Hannanum()
    start_time = time.time()
    
    # Morphèmes
    morphs = hannanum.morphs(sample_text)
    # POS tagging
    pos = hannanum.pos(sample_text)
    # Noms
    nouns = hannanum.nouns(sample_text)
    
    elapsed = time.time() - start_time
    
    result_hannanum = {
        "analyzer": "Hannanum",
        "sample_title": sample_speech["title"],
        "sample_text_length": len(sample_text),
        "execution_time_seconds": round(elapsed, 3),
        "morphemes_count": len(morphs),
        "morphemes_sample": morphs[:20],
        "pos_count": len(pos),
        "pos_sample": pos[:20],
        "nouns_count": len(nouns),
        "nouns_sample": nouns[:20]
    }
    
    print(f"   ✓ Temps d'exécution: {elapsed:.3f} secondes")
    print(f"   ✓ Morphèmes trouvés: {len(morphs)}")
    print(f"   ✓ Noms trouvés: {len(nouns)}")
    print(f"   Exemple morphèmes: {morphs[:10]}")
    print(f"   Exemple noms: {nouns[:10]}")
    
    # Sauvegarder
    with open("nlp_result_hannanum.json", "w", encoding="utf-8") as f:
        json.dump(result_hannanum, f, ensure_ascii=False, indent=2)
    print("   💾 Résultats sauvegardés: nlp_result_hannanum.json")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# ========== KKMA ==========
print("\n🔍 Test 2/3: Kkma")
print("-" * 80)
try:
    kkma = Kkma()
    start_time = time.time()
    
    # Morphèmes
    morphs = kkma.morphs(sample_text)
    # POS tagging
    pos = kkma.pos(sample_text)
    # Noms
    nouns = kkma.nouns(sample_text)
    # Phrases (spécifique à Kkma)
    sentences = kkma.sentences(sample_text)
    
    elapsed = time.time() - start_time
    
    result_kkma = {
        "analyzer": "Kkma",
        "sample_title": sample_speech["title"],
        "sample_text_length": len(sample_text),
        "execution_time_seconds": round(elapsed, 3),
        "morphemes_count": len(morphs),
        "morphemes_sample": morphs[:20],
        "pos_count": len(pos),
        "pos_sample": pos[:20],
        "nouns_count": len(nouns),
        "nouns_sample": nouns[:20],
        "sentences_count": len(sentences),
        "sentences_sample": sentences[:3]
    }
    
    print(f"   ✓ Temps d'exécution: {elapsed:.3f} secondes")
    print(f"   ✓ Morphèmes trouvés: {len(morphs)}")
    print(f"   ✓ Noms trouvés: {len(nouns)}")
    print(f"   ✓ Phrases détectées: {len(sentences)}")
    print(f"   Exemple morphèmes: {morphs[:10]}")
    print(f"   Exemple noms: {nouns[:10]}")
    
    # Sauvegarder
    with open("nlp_result_kkma.json", "w", encoding="utf-8") as f:
        json.dump(result_kkma, f, ensure_ascii=False, indent=2)
    print("   💾 Résultats sauvegardés: nlp_result_kkma.json")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# ========== KOMORAN ==========
print("\n🔍 Test 3/3: Komoran")
print("-" * 80)
try:
    komoran = Komoran()
    start_time = time.time()
    
    # Morphèmes
    morphs = komoran.morphs(sample_text)
    # POS tagging
    pos = komoran.pos(sample_text)
    # Noms
    nouns = komoran.nouns(sample_text)
    
    elapsed = time.time() - start_time
    
    result_komoran = {
        "analyzer": "Komoran",
        "sample_title": sample_speech["title"],
        "sample_text_length": len(sample_text),
        "execution_time_seconds": round(elapsed, 3),
        "morphemes_count": len(morphs),
        "morphemes_sample": morphs[:20],
        "pos_count": len(pos),
        "pos_sample": pos[:20],
        "nouns_count": len(nouns),
        "nouns_sample": nouns[:20]
    }
    
    print(f"   ✓ Temps d'exécution: {elapsed:.3f} secondes")
    print(f"   ✓ Morphèmes trouvés: {len(morphs)}")
    print(f"   ✓ Noms trouvés: {len(nouns)}")
    print(f"   Exemple morphèmes: {morphs[:10]}")
    print(f"   Exemple noms: {nouns[:10]}")
    
    # Sauvegarder
    with open("nlp_result_komoran.json", "w", encoding="utf-8") as f:
        json.dump(result_komoran, f, ensure_ascii=False, indent=2)
    print("   💾 Résultats sauvegardés: nlp_result_komoran.json")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# ========== RÉSUMÉ ==========
print("\n" + "="*80)
print("📊 COMPARAISON TERMINÉE")
print("="*80)
print("\nFichiers de résultats créés:")
print("  • nlp_result_hannanum.json")
print("  • nlp_result_kkma.json")
print("  • nlp_result_komoran.json")
print("\nConsultez ces fichiers pour voir les détails et temps d'exécution!")
