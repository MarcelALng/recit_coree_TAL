#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse linguistique des exports XML TXM
Calcule des statistiques de corpus, distribution PoS et diversité lexicale
"""

import os
import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd

def analyze_xml_file(file_path):
    """Analyse un fichier XML TXM et retourne ses statistiques"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {file_path}: {e}")
        return None

    stats = {
        'president': '',
        'total_texts': 0,
        'total_paragraphs': 0,
        'total_sentences': 0,
        'total_tokens': 0,
        'unique_tokens': 0,
        'pos_distribution': Counter(),
        'top_nouns': Counter(),
        'top_verbs': Counter()
    }

    # Récupérer le nom du président du premier texte
    first_text = root.find('text')
    if first_text is not None:
        stats['president'] = first_text.get('president', 'Inconnu')

    all_tokens = []

    for text in root.findall('text'):
        stats['total_texts'] += 1
        for p in text.findall('p'):
            stats['total_paragraphs'] += 1
            for s in p.findall('s'):
                stats['total_sentences'] += 1
                for w in s.findall('w'):
                    stats['total_tokens'] += 1
                    word = w.text if w.text else ""
                    pos = w.get('pos', 'UNK')
                    
                    stats['pos_distribution'][pos] += 1
                    all_tokens.append(word)
                    
                    # Noms communs (NNG) ou propres (NNP)
                    if pos in ['NNG', 'NNP'] and len(word) > 1:
                        stats['top_nouns'][word] += 1
                    # Verbes (VV)
                    elif pos == 'VV' and len(word) > 1:
                        stats['top_verbs'][word] += 1

    stats['unique_tokens'] = len(set(all_tokens))
    # Type-Token Ratio
    stats['ttr'] = (stats['unique_tokens'] / stats['total_tokens']) * 100 if stats['total_tokens'] > 0 else 0
    
    return stats

def main():
    xml_dir = "txm_export"
    if not os.path.exists(xml_dir):
        print(f"❌ Dossier {xml_dir} introuvable.")
        return

    results = []
    files = sorted([f for f in os.listdir(xml_dir) if f.endswith('.xml')])
    
    print(f"🚀 Analyse de {len(files)} fichiers XML dans {xml_dir}...")
    
    for filename in files:
        file_path = os.path.join(xml_dir, filename)
        print(f"  • {filename}...", end='\r')
        stats = analyze_xml_file(file_path)
        if stats:
            results.append(stats)
    
    print("\n✅ Analyse terminée.\n")

    # Affichage du tableau récapitulatif
    summary_data = []
    for r in results:
        summary_data.append({
            'Président': r['president'],
            'Discours': r['total_texts'],
            'Phrases': r['total_sentences'],
            'Mots (Tokens)': r['total_tokens'],
            'Vocabulaire (Types)': r['unique_tokens'],
            'Diversité (TTR %)': f"{r['ttr']:.2f}%"
        })
    
    df_summary = pd.DataFrame(summary_data)
    print("📊 STATISTIQUES GLOBALES PAR PRÉSIDENT")
    print("=" * 100)
    print(df_summary.to_string(index=False))
    print("=" * 100)

    # Top 5 noms pour chaque président
    print("\n🏆 TOP 5 NOMS (NNG/NNP) PAR PRÉSIDENT")
    print("-" * 100)
    for r in results:
        top_n = ", ".join([f"{w}({c})" for w, c in r['top_nouns'].most_common(5)])
        print(f"{r['president']:<20} : {top_n}")

if __name__ == "__main__":
    main()
