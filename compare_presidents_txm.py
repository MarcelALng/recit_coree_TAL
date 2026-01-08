#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse Comparative Inter-Présidents
Recherche les points communs (stabilité lexicale) et les différences (variance lexicale)
Génère un rapport CSV récapitulatif.
"""

import os
import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd
import numpy as np

def extract_all_frequencies(xml_dir):
    """Extrait les fréquences de mots pour tous les présidents"""
    data = {}
    total_words_per_president = {}
    
    files = [f for f in os.listdir(xml_dir) if f.endswith('.xml')]
    
    for filename in files:
        file_path = os.path.join(xml_dir, filename)
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Identifier le président
        first_text = root.find('text')
        president = first_text.get('president', filename.replace('.xml', ''))
        
        counts = Counter()
        size = 0
        for w in root.findall('.//w'):
            pos = w.get('pos', 'UNK')
            word = w.text if w.text else ""
            if pos in ['NNG', 'NNP'] and len(word) > 1:
                counts[word] += 1
                size += 1
        
        data[president] = counts
        total_words_per_president[president] = size
        
    return data, total_words_per_president

def analyze_comparison(data, sizes):
    """Analyse les points communs et les différences"""
    # Créer un DataFrame avec tous les mots
    all_words = set()
    for counts in data.values():
        all_words.update(counts.keys())
    
    df = pd.DataFrame(index=list(all_words))
    
    # Remplir avec les fréquences relatives (pour 100 000 mots)
    for president, counts in data.items():
        norm_factor = 100000 / sizes[president]
        df[president] = df.index.map(lambda x: counts.get(x, 0) * norm_factor)
    
    # Calculer moyenne, écart-type et coefficient de variation (CV = std/mean)
    df['mean'] = df.mean(axis=1)
    df['std'] = df.std(axis=1)
    # On évite la division par zéro
    df['cv'] = df['std'] / df['mean']
    
    # Filtrer les mots trop rares (< 5 occurrences moyennes pour 100k) pour éviter le bruit
    df_filtered = df[df['mean'] > 5].copy()
    
    # Points communs : CV le plus faible (utilisés de manière stable par tous)
    commonalities = df_filtered.sort_values('cv').head(10)
    
    # Points de différence : CV le plus élevé (très fluctuants selon les présidents)
    # On cherche des mots qui sont très fréquents chez certains mais absents chez d'hui
    differences = df_filtered.sort_values('cv', ascending=False).head(10)
    
    return commonalities, differences, df

def main():
    xml_dir = "txm_export"
    if not os.path.exists(xml_dir):
        print(f"❌ Dossier {xml_dir} introuvable.")
        return

    print("📊 Lecture du corpus XML et extraction des données...")
    data, sizes = extract_all_frequencies(xml_dir)
    
    print("✨ Calcul des statistiques comparatives...")
    commons, diffs, full_df = analyze_comparison(data, sizes)
    
    # Préparer le CSV
    results = []
    
    print("\n🤝 POINTS COMMUNS (Stabilité lexicale - Top 3)")
    for i, (word, row) in enumerate(commons.head(3).iterrows()):
        results.append({'Type': 'Point Commun', 'Terme': word, 'Score_CV': row['cv'], 'Freq_Moyenne_100k': row['mean']})
        print(f"  {i+1}. {word} (Utilisé de manière très stable par tous les présidents)")

    print("\n⚡ POINTS DE DIFFÉRENCE (Contraste lexical - Top 3)")
    for i, (word, row) in enumerate(diffs.head(3).iterrows()):
        results.append({'Type': 'Différence Majeure', 'Terme': word, 'Score_CV': row['cv'], 'Freq_Moyenne_100k': row['mean']})
        print(f"  {i+1}. {word} (Très spécifique à certains mandats, absent chez d'autres)")

    # Sauvegarde CSV
    results_df = pd.DataFrame(results)
    output_file = "president_comparison_results.csv"
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Résultats complets exportés dans : {output_file}")

if __name__ == "__main__":
    main()
