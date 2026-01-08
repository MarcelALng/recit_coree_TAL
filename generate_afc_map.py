import os
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from googletrans import Translator

def perform_ca(df):
    """
    Perform Correspondence Analysis (CA) using SVD.
    df: Contingency table (Words as rows, Presidents as columns)
    """
    # 1. Correspondence Matrix P
    N = df.values
    n = N.sum()
    P = N / n
    
    # 2. Row and Column Profiles (Sums)
    r = P.sum(axis=1) # Row sums
    c = P.sum(axis=0) # Column sums
    
    # 3. Standardized Residuals S
    # S = (P - r*c.T) / sqrt(r * c.T)
    # Using matrix operations:
    Dr_inv_sqrt = np.diag(1.0 / np.sqrt(r))
    Dc_inv_sqrt = np.diag(1.0 / np.sqrt(c))
    
    # Residuals = P - np.outer(r, c)
    S = Dr_inv_sqrt @ (P - np.outer(r, c)) @ Dc_inv_sqrt
    
    # 4. SVD
    U, Sigma, Vt = np.linalg.svd(S, full_matrices=False)
    
    # 5. Row and Column coordinates
    # Rows: F = Dr^-1/2 * U * Sigma
    row_coords = Dr_inv_sqrt @ U @ np.diag(Sigma)
    
    # Columns: G = Dc^-1/2 * V * Sigma (V is Vt.T)
    col_coords = Dc_inv_sqrt @ Vt.T @ np.diag(Sigma)
    
    # Explained variance
    eigenvalues = Sigma**2
    total_inertia = eigenvalues.sum()
    explained_variance = (eigenvalues / total_inertia) * 100
    
    return row_coords, col_coords, explained_variance

def generate_afc(xml_dir, output_img):
    presidents_chrono = [
        'Lee_Seung_Man', 'Yun_Bo_Seon', 'Park_Chung_Hee', 'Choi_Kyu_Hah',
        'Chun_Doo_Hwan', 'Roh_Tae_Woo', 'Kim_Young_Sam', 'Kim_Dae_Jung',
        'Roh_Moo_Hyun', 'Lee_Myung_Bak', 'Park_Geun_Hye', 'Moon_Jae_In'
    ]
    
    word_counts = {}
    all_words = Counter()
    
    print("Parsing XML exports...")
    for pres_id in presidents_chrono:
        filename = f"{pres_id}.xml"
        path = os.path.join(xml_dir, filename)
        if not os.path.exists(path):
            continue
            
        tree = ET.parse(path)
        root = tree.getroot()
        
        counts = Counter()
        for word in root.findall('.//w'):
            pos = word.get('pos')
            text = word.text
            # Use nouns and verbs as features
            if pos in ['NNG', 'NNP', 'VV'] and text and len(text) > 1:
                counts[text] += 1
                all_words[text] += 1
        
        word_counts[pres_id] = counts

    # Select top N words for clarity (important for AFC stability)
    top_n = 100
    top_vocab = [w for w, c in all_words.most_common(top_n)]
    
    # Build Contingency Table
    data = []
    for word in top_vocab:
        row = [word_counts[pres].get(word, 0) for pres in presidents_chrono if pres in word_counts]
        data.append(row)
        
    actual_presidents = [p.replace('_', ' ') for p in presidents_chrono if p in word_counts]
    df = pd.DataFrame(data, index=top_vocab, columns=actual_presidents)
    
    print("Calculating AFC...")
    row_coords, col_coords, exp_var = perform_ca(df)
    
    # Translate labels to French
    print("Translating labels to French...")
    translator = Translator()
    translated_words = []
    for w in top_vocab:
        try:
            # Short manual cache for common terms to speed up
            manual = {
                '국민': 'Peuple', '경제': 'Économie', '민주주의': 'Démocratie', 
                '통일': 'Unification', '평화': 'Paix', '정부': 'Gouvernement',
                '건설': 'Construction', '사회': 'Société', '대한민국': 'République',
                '하다': 'Faire', '되다': 'Devenir'
            }
            if w in manual:
                translated_words.append(manual[w])
            else:
                trans = translator.translate(w, src='ko', dest='fr').text
                clean_trans = trans.encode('ascii', 'ignore').decode('ascii').strip()
                translated_words.append(clean_trans if clean_trans else "Terme")
        except:
            translated_words.append("???")

    # Plot
    plt.figure(figsize=(14, 12))
    plt.axhline(0, color='grey', lw=1, ls='--')
    plt.axvline(0, color='grey', lw=1, ls='--')
    
    # 1. Plot Presidents (Columns) in Red
    plt.scatter(col_coords[:, 0], col_coords[:, 1], color='red', s=100, label='Présidents')
    for i, pres in enumerate(actual_presidents):
        plt.annotate(pres, (col_coords[i, 0], col_coords[i, 1]), 
                     color='red', fontsize=12, fontweight='bold', ha='center', va='bottom')
        
    # 2. Plot Words (Rows) in Blue
    # Only plot words with high contribution (furthest from origin) for readability
    dist = np.sqrt(row_coords[:, 0]**2 + row_coords[:, 1]**2)
    top_contrib_indices = dist.argsort()[-50:] # Top 50 words
    
    plt.scatter(row_coords[top_contrib_indices, 0], row_coords[top_contrib_indices, 1], 
                color='blue', alpha=0.3, s=20)
    for i in top_contrib_indices:
        plt.annotate(translated_words[i], (row_coords[i, 0], row_coords[i, 1]), 
                     color='blue', fontsize=9, alpha=0.7)
        
    plt.title(f"Analyse Factorielle des Correspondances (Presidents vs Mots)\n"
              f"Axe 1: {exp_var[0]:.1f}% | Axe 2: {exp_var[1]:.1f}%", fontsize=15)
    plt.xlabel(f"Dimension 1 ({exp_var[0]:.1f}%)")
    plt.ylabel(f"Dimension 2 ({exp_var[1]:.1f}%)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_img, dpi=150)
    print(f"AFC Map saved to {output_img}")

if __name__ == "__main__":
    generate_afc("txm_export", "lexical_afc_map.png")
