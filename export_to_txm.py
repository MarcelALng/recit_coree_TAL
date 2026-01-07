#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Export des discours présidentiels pour TXM
Format: un XML par président, avec segmentation en phrases et PoS tagging (Kkma)
"""

import json
import os
import time
import argparse
from konlpy.tag import Kkma
from xml.sax.saxutils import escape

# Liste des présidents (ID du fichier, Nom complet)
PRESIDENTS = [
    ('Lee_Seung_Man', 'Lee Seung Man'),
    ('Yun_Bo_Seon', 'Yun Bo Seon'),
    ('Park_Chung_Hee', 'Park Chung Hee'),
    ('Choi_Kyu_Hah', 'Choi Kyu Hah'),
    ('Chun_Doo_Hwan', 'Chun Doo Hwan'),
    ('Roh_Tae_Woo', 'Roh Tae Woo'),
    ('Kim_Young_Sam', 'Kim Young Sam'),
    ('Kim_Dae_Jung', 'Kim Dae Jung'),
    ('Roh_Moo_Hyun', 'Roh Moo Hyun'),
    ('Lee_Myung_Bak', 'Lee Myung Bak'),
    ('Park_Geun_Hye', 'Park Geun Hye'),
    ('Moon_Jae_In', 'Moon Jae In')
]

def clean_xml_attr(text):
    """Prépare un texte pour être utilisé comme valeur d'attribut XML"""
    if not text:
        return ""
    return escape(text).replace('"', "&quot;").replace("'", "&apos;")

def export_president_to_txm(file_id, president_name, output_dir, limit=None):
    """Analyse et exporte les discours d'un président vers un fichier XML"""
    input_file = f"president_texts_{file_id}.json"
    output_file = os.path.join(output_dir, f"{file_id}.xml")
    
    if not os.path.exists(input_file):
        print(f"⚠️  Fichier {input_file} introuvable.")
        return

    print(f"\n📂 Traitement de {president_name}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        speeches = json.load(f)
    
    if limit:
        speeches = speeches[:limit]
        print(f"  (Limité aux {limit} premiers discours)")

    kkma = Kkma()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # En-tête XML minimaliste pour TXM
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<corpus>\n')
        
        for i, speech in enumerate(speeches, 1):
            title = clean_xml_attr(speech.get('title', ''))
            date = clean_xml_attr(speech.get('date', ''))
            url = clean_xml_attr(speech.get('url', ''))
            
            # Attributs de texte pour les métadonnées TXM
            f.write(f'  <text title="{title}" date="{date}" url="{url}" president="{clean_xml_attr(president_name)}">\n')
            
            for p_idx, paragraph in enumerate(speech['paragraphs'], 1):
                if not paragraph.strip():
                    continue
                
                f.write(f'    <p id="p{p_idx}">\n')
                
                try:
                    # Segmentation en phrases
                    sentences = kkma.sentences(paragraph)
                    for s_idx, sentence in enumerate(sentences, 1):
                        f.write(f'      <s id="s{s_idx}">\n')
                        
                        # PoS Tagging
                        # pos format: [(word, tag), ...]
                        tags = kkma.pos(sentence)
                        for word, tag in tags:
                            # Échapper le contenu du mot
                            safe_word = escape(word)
                            f.write(f'        <w pos="{tag}">{safe_word}</w>\n')
                        
                        f.write('      </s>\n')
                except Exception as e:
                    print(f"  ❌ Erreur sur un paragraphe du discours {i}: {e}")
                    # En cas d'erreur massive, on écrit le paragraphe brut
                    f.write(f'      {escape(paragraph)}\n')
                
                f.write('    </p>\n')
            
            f.write('  </text>\n')
            if i % 10 == 0:
                print(f"    - {i}/{len(speeches)} discours traités...")
        
        f.write('</corpus>\n')
    
    print(f"   ✓ Exporté vers {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Export presidential speeches to TXM XML format")
    parser.add_argument("--limit", type=int, help="Limit number of speeches per president (for testing)")
    parser.add_argument("--president", type=str, help="Specific president to export (Lee_Seung_Man, etc.)")
    args = parser.parse_args()

    output_dir = "txm_export"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Dossier {output_dir} créé.")

    start_time = time.time()
    
    if args.president:
        pres = next((p for p in PRESIDENTS if p[0] == args.president), None)
        if pres:
            export_president_to_txm(pres[0], pres[1], output_dir, limit=args.limit)
        else:
            print(f"❌ Président inconnu: {args.president}")
    else:
        for file_id, president_name in PRESIDENTS:
            export_president_to_txm(file_id, president_name, output_dir, limit=args.limit)

    total_time = time.time() - start_time
    print(f"\n✨ Terminé en {total_time:.2f} secondes.")

if __name__ == "__main__":
    main()
