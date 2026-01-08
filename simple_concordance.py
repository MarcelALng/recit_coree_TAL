#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse de Concordance Simple (KWIC) - Simulation TXM
Recherche un mot-clé dans les fichiers JSON du dossier 'texte president'
"""

import json
import os
import argparse
from termcolor import colored

def get_concordance(keyword, folder_path, context_size=50):
    """Effectue une recherche de concordance pour un mot-clé donné"""
    results = []
    
    # Lister les fichiers JSON
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    print(f"🔍 Recherche de concordance pour : '{keyword}'")
    print("-" * 100)
    
    count = 0
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        president = filename.replace("president_texts_", "").replace(".json", "").replace("_", " ")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            speeches = json.load(f)
            
        for speech in speeches:
            date = speech.get('date', 'Unknown')
            for paragraph in speech.get('paragraphs', []):
                # Recherche insensible à la casse pour le coréen? (pas vraiment de casse)
                # Mais on cherche l'index
                start = 0
                while True:
                    idx = paragraph.find(keyword, start)
                    if idx == -1:
                        break
                    
                    count += 1
                    # Extraire le contexte
                    left_context = paragraph[max(0, idx - context_size):idx].replace("\n", " ")
                    right_context = paragraph[idx + len(keyword):idx + len(keyword) + context_size].replace("\n", " ")
                    
                    # Formater pour l'affichage
                    results.append({
                        'president': president,
                        'date': date,
                        'left': left_context.rjust(context_size),
                        'keyword': keyword,
                        'right': right_context.ljust(context_size)
                    })
                    
                    start = idx + 1
                    
                    # Limiter l'affichage à 100 résultats pour le test
                    if count >= 100:
                        break
                if count >= 100:
                    break
            if count >= 100:
                break
        if count >= 100:
            break

    # Affichage des résultats
    print(f"{'PRÉSIDENT':<20} | {'DATE':<12} | {'CONCORDANCE (KWIC)'}")
    print("=" * 120)
    for res in results:
        # Utiliser des couleurs si possible si on lance manuellement, 
        # mais ici on va juste imprimer proprement
        kw_colored = f"[{res['keyword']}]"
        print(f"{res['president']:<20} | {res['date']:<12} | ...{res['left']} {kw_colored} {res['right']}...")

    print("-" * 120)
    print(f"Total des occurrences trouvées (limit à 100) : {count}")

def main():
    parser = argparse.ArgumentParser(description="Analyse de concordance simple sur les discours présidentiels")
    parser.add_argument("keyword", help="Le mot-clé à rechercher")
    parser.add_argument("--folder", default="texte president", help="Dossier contenant les fichiers JSON")
    parser.add_argument("--context", type=int, default=40, help="Taille du contexte (caractères)")
    args = parser.parse_args()

    if not os.path.exists(args.folder):
        print(f"❌ Dossier introuvable : {args.folder}")
        return

    get_concordance(args.keyword, args.folder, args.context)

if __name__ == "__main__":
    main()
