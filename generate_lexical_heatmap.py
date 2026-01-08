import os
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import hypergeom
from collections import Counter

def calculate_specificity(f_sub, n_sub, f_total, n_total):
    # Lafon's index: -log10(p-value)
    # p = P(X >= f_sub)
    # hypergeom.sf(k-1, M, n, N) where:
    # M = total population (tokens in corpus)
    # n = total successes (occurrences of word in corpus)
    # N = sample size (tokens in sub-corpus)
    # k = observed successes (occurrences of word in sub-corpus)
    p_val = hypergeom.sf(f_sub - 1, n_total, f_total, n_sub)
    if p_val <= 0:
        return 100 # Cap the score
    return -np.log10(p_val)

def generate_heatmap(xml_dir, output_img):
    presidents = []
    word_counts = {} # president -> word -> count
    total_tokens = {} # president -> total
    
    global_counts = Counter()
    global_total = 0
    
    PRESIDENTS_CHRONO = [
        'Lee_Seung_Man', 'Yun_Bo_Seon', 'Park_Chung_Hee', 'Choi_Kyu_Hah',
        'Chun_Doo_Hwan', 'Roh_Tae_Woo', 'Kim_Young_Sam', 'Kim_Dae_Jung',
        'Roh_Moo_Hyun', 'Lee_Myung_Bak', 'Park_Geun_Hye', 'Moon_Jae_In'
    ]
    
    # 1. Parse all XMLs
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
        tokens = 0
        for word in root.findall('.//w'):
            pos = word.get('pos')
            text = word.text
            # Only common nouns (NNG) and proper nouns (NNP) for thematic analysis
            if pos in ['NNG', 'NNP'] and len(text) > 1:
                counts[text] += 1
                global_counts[text] += 1
            tokens += 1
            
        word_counts[pres_name] = counts
        total_tokens[pres_name] = tokens
        global_total += tokens

    # 3. Create Matrix with Translations
    TRANSLATIONS = {
        '국민': 'Peuple', '경제': 'Économie', '민주주의': 'Démocratie', '평화': 'Paix',
        '북한': 'Corée du Nord', '건설': 'Construction', '발전': 'Développement',
        '안정': 'Stabilité', '노력': 'Effort', '개혁': 'Réforme', '통일': 'Unification',
        '협력': 'Coopération', '극복': 'Surmonter', '세계': 'Monde', '미래': 'Avenir',
        '문화': 'Culture', '교육': 'Éducation', '복지': 'Bien-être', '위기': 'Crise',
        '일본': 'Japon', '미국': 'USA', '독도': 'Dokdo', '취임': 'Inauguration',
        '선거': 'Élection', '헌법': 'Constitution', '자유': 'Liberté', '정의': 'Justice',
        '혁명': 'Révolution', '과학': 'Science', '기술': 'Technique', '일자리': 'Emploi',
        '청년': 'Jeunesse', '여성': 'Femmes', '환경': 'Environnement', '에너지': 'Énergie',
        '코로나': 'Corona', '백신': 'Vaccin', '방역': 'Quarantaine', '새마을': 'Saemaul',
        '근대화': 'Modernisation', '자립': 'Autonomie', '수출': 'Exportation',
        '산업': 'Industrie', '정부': 'Gouvernement', '사회': 'Société', '국가': 'État',
        '정치': 'Politique', '외환': 'Devises', '아이엠에프': 'FMI', '고용': 'Emploi',
        '구조': 'Structure', '조정': 'Ajustement', '창조': 'Création', '혁신': 'Innovation',
        '규제': 'Régulation', '햇볕': 'Soleil (Sunshine)', '교류': 'Échanges'
    }
    
    # Identify top 5 specific words per president
    top_words = set()
    for pres in presidents:
        specs = []
        n_sub = total_tokens[pres]
        for word, f_sub in word_counts[pres].items():
            f_total = global_counts[word]
            score = calculate_specificity(f_sub, n_sub, f_total, global_total)
            specs.append((word, score))
        
        specs.sort(key=lambda x: x[1], reverse=True)
        for w, s in specs[:5]:
            top_words.add(w)
            
    top_words_list = sorted(list(top_words))
    
    # Use googletrans for anything missing in manual TRANSLATIONS
    print("Translating labels...")
    from googletrans import Translator
    translator = Translator()
    
    clean_labels = []
    for w in top_words_list:
        if w in TRANSLATIONS:
            clean_labels.append(TRANSLATIONS[w])
        else:
            try:
                trans = translator.translate(w, src='ko', dest='fr').text
                # Clean non-ascii just in case
                clean_trans = trans.encode('ascii', 'ignore').decode('ascii').strip()
                if not clean_trans: clean_trans = "Concept"
                clean_labels.append(clean_trans)
                # Proactively update TRANSLATIONS for next time if we were saving it
                TRANSLATIONS[w] = clean_trans
            except:
                clean_labels.append("Terme")
    
    matrix_data = []
    for word in top_words_list:
        row = []
        f_total = global_counts[word]
        for pres in presidents:
            f_sub = word_counts[pres].get(word, 0)
            n_sub = total_tokens[pres]
            score = calculate_specificity(f_sub, n_sub, f_total, global_total)
            row.append(score)
        matrix_data.append(row)
        
    df_heatmap = pd.DataFrame(matrix_data, index=clean_labels, columns=presidents)
    
    # 4. Plot
    plt.figure(figsize=(15, 12))
    sns.heatmap(df_heatmap, annot=False, cmap="YlOrRd", cbar_kws={'label': "Indice de spécificité (-log10 p)"})
    plt.title("Évolution des Thématiques Présidentielles (1948-2022) - Heatmap de Spécificité")
    plt.xlabel("Mandats Présidentiels")
    plt.ylabel("Concepts Clés (Traduits)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_img)
    print(f"Heatmap saved to {output_img}")

if __name__ == "__main__":
    XML_DIR = "txm_export"
    OUTPUT = "lexical_heatmap.png"
    generate_heatmap(XML_DIR, OUTPUT)
