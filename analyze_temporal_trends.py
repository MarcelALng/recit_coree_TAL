import os
import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

def analyze_temporal_trends(xml_dir, target_words, output_img):
    presidents = []
    data = {word: [] for word in target_words.keys()}
    
    # Mapping Korean target words to their French labels
    # target_words = {'민주주의': 'Démocratie', ...}
    
    PRESIDENTS_CHRONO = [
        'Lee_Seung_Man', 'Yun_Bo_Seon', 'Park_Chung_Hee', 'Choi_Kyu_Hah',
        'Chun_Doo_Hwan', 'Roh_Tae_Woo', 'Kim_Young_Sam', 'Kim_Dae_Jung',
        'Roh_Moo_Hyun', 'Lee_Myung_Bak', 'Park_Geun_Hye', 'Moon_Jae_In'
    ]
    
    for filename_base in PRESIDENTS_CHRONO:
        filename = f"{filename_base}.xml"
        path = os.path.join(xml_dir, filename)
        if not os.path.exists(path):
            continue
            
        pres_name = filename_base.replace('_', ' ')
        presidents.append(pres_name)
        
        tree = ET.parse(path)
        root = tree.getroot()
        
        counts = Counter()
        total_tokens = 0
        for word in root.findall('.//w'):
            text = word.text
            if text in target_words:
                counts[text] += 1
            total_tokens += 1
            
        for k_word in target_words.keys():
            # Frequency per 10,000 tokens
            freq = (counts[k_word] / total_tokens) * 10000 if total_tokens > 0 else 0
            data[k_word].append(freq)
            
    # Plotting
    plt.figure(figsize=(12, 7))
    for k_word, f_label in target_words.items():
        plt.plot(presidents, data[k_word], marker='o', label=f_label)
        
    plt.title("Évolution Temporelle des Concepts Clés (1948-2022)")
    plt.xlabel("Mandats Présidentiels")
    plt.ylabel("Fréquence relative (pour 10 000 mots)")
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_img)
    print(f"Trends plot saved to {output_img}")

if __name__ == "__main__":
    XML_DIR = "txm_export"
    # Select key diachronic concepts
    TARGETS = {
        '민주주의': 'Démocratie',
        '통일': 'Unification',
        '경제': 'Économie',
        '자유': 'Liberté',
        '평화': 'Paix'
    }
    analyze_temporal_trends(XML_DIR, TARGETS, "temporal_trends.png")
