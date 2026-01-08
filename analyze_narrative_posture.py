import os
import xml.etree.ElementTree as ET
import pandas as pd
from collections import Counter

def analyze_narrative_posture(xml_dir):
    results = []
    
    # Define Pronoun lists (1st person)
    # 1st Person Singular: 나 (Na), 저 (Jeo)
    SINGULAR_PRONOUNS = ['나', '저']
    # 1st Person Plural: 우리 (Uri), 저희 (Jeohui)
    PLURAL_PRONOUNS = ['우리', '저희']
    
    for filename in sorted(os.listdir(xml_dir)):
        if not filename.endswith('.xml'):
            continue
            
        path = os.path.join(xml_dir, filename)
        president = filename.replace('.xml', '').replace('_', ' ')
        
        print(f"Analyzing {president}...")
        
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            continue
            
        stats = {
            'President': president,
            'I_Singular': 0,
            'We_Plural': 0,
            'Action_Verbs_VV': 0,
            'State_Verbs_VA': 0,
            'Total_Tokens': 0
        }
        
        for word in root.findall('.//w'):
            pos = word.get('pos')
            text = word.text
            stats['Total_Tokens'] += 1
            
            if pos == 'NP':
                if text in SINGULAR_PRONOUNS:
                    stats['I_Singular'] += 1
                elif text in PLURAL_PRONOUNS:
                    stats['We_Plural'] += 1
            elif pos == 'VV':
                stats['Action_Verbs_VV'] += 1
            elif pos == 'VA':
                stats['State_Verbs_VA'] += 1
                
        # Calculate Ratios
        stats['I_per_1000'] = (stats['I_Singular'] / stats['Total_Tokens']) * 1000 if stats['Total_Tokens'] > 0 else 0
        stats['We_per_1000'] = (stats['We_Plural'] / stats['Total_Tokens']) * 1000 if stats['Total_Tokens'] > 0 else 0
        stats['Action_ratio'] = stats['Action_Verbs_VV'] / (stats['Action_Verbs_VV'] + stats['State_Verbs_VA']) if (stats['Action_Verbs_VV'] + stats['State_Verbs_VA']) > 0 else 0
        
        results.append(stats)
        
    return pd.DataFrame(results)

if __name__ == "__main__":
    XML_DIR = "txm_export"
    df = analyze_narrative_posture(XML_DIR)
    
    output_path = "narrative_posture_results.csv"
    df.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}")
    print(df[['President', 'I_per_1000', 'We_per_1000', 'Action_ratio']])
