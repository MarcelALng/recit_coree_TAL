#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse de Spécificité TXM (Indice de Lafon)
Calcule les termes sur-représentés par président en utilisant la loi hypergéométrique.
"""

import os
import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd
import numpy as np
from scipy.stats import hypergeom
import math

def extract_counts(xml_dir):
    """Extrait les fréquences de mots par président et au total"""
    presidents_counts = {}
    total_counts = Counter()
    corpus_size = 0
    president_sizes = {}

    files = [f for f in os.listdir(xml_dir) if f.endswith('.xml')]
    
    for filename in files:
        file_path = os.path.join(xml_dir, filename)
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Identifier le président
        first_text = root.find('text')
        president = first_text.get('president', filename.replace('.xml', '')) if first_text is not None else filename.replace('.xml', '')
        
        p_counts = Counter()
        p_size = 0
        
        for w in root.findall('.//w'):
            pos = w.get('pos', 'UNK')
            word = w.text if w.text else ""
            
            # On se concentre sur les noms significatifs (longueur > 1)
            if pos in ['NNG', 'NNP'] and len(word) > 1:
                p_counts[word] += 1
                total_counts[word] += 1
                p_size += 1
                corpus_size += 1
                
        presidents_counts[president] = p_counts
        president_sizes[president] = p_size
        
    return presidents_counts, total_counts, president_sizes, corpus_size

def calculate_specificity(f, t, n, N):
    """
    Calcule l'indice de spécificité (Lafon)
    f : fréquence du mot dans la partie (sub-corpus)
    t : fréquence du mot dans le corpus total
    n : taille de la partie (nombre total de mots dans la partie)
    N : taille du corpus total
    
    Retourne -log10(P(X >= f))
    """
    # sf_val = hypergeom.sf(f-1, N, t, n) # Probabilité P(X >= f)
    # L'indice de spécificité TXM est souvent exprimé comme -log10(p)
    # Pour éviter les problèmes d'arrondi avec sf (valeurs proches de 0), 
    # on utilise logSF si disponible ou on gère les cas extrêmes.
    
    log_p = hypergeom.logsf(f - 1, N, t, n) / math.log(10)
    return -log_p

def main():
    xml_dir = "txm_export"
    if not os.path.exists(xml_dir):
        print(f"❌ Dossier {xml_dir} introuvable.")
        return

    print("📊 Extraction des fréquences (Nouns NNG/NNP)...")
    p_counts, t_counts, p_sizes, N = extract_counts(xml_dir)
    
    print(f"✅ Taille du corpus traité : {N} noms.")
    print(f"✨ Calcul des spécificités pour {len(p_counts)} présidents...\n")

    results = {}
    
    for president, counts in p_counts.items():
        n = p_sizes[president]
        spec_scores = []
        
        # On ne traite que les mots qui apparaissent au moins 5 fois chez le président
        for word, f in counts.items():
            if f >= 5:
                t = t_counts[word]
                score = calculate_specificity(f, t, n, N)
                spec_scores.append((word, f, score))
        
        # Trier par score décroissant (les plus spécifiques en premier)
        spec_scores.sort(key=lambda x: x[2], reverse=True)
        results[president] = spec_scores[:10] # Top 10 pour l'analyse
        
    # Affichage du rapport
    print(f"{'PRÉSIDENT':<20} | {'TOP 5 TERMES SPÉCIFIQUES (Indice TXM)'}")
    print("=" * 100)
    
    for president in sorted(results.keys()):
        top_5 = results[president][:5]
        # Formater l'affichage : Mot (indice)
        formatted = "  ".join([f"{word} ({score:.1f})" for word, f, score in top_5])
        print(f"{president:<20} | {formatted}")

if __name__ == "__main__":
    main()
