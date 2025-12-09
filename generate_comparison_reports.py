#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Génère des fichiers markdown de comparaison pour chaque président
"""

import json
import glob

def create_comparison_md(json_file):
    """Crée un fichier markdown de comparaison à partir du JSON"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    president = data['president']
    total_speeches = data['total_speeches']
    results = data['results']
    
    # Extraire les données
    hannanum = next(r for r in results if r['analyzer'] == 'Hannanum')
    kkma = next(r for r in results if r['analyzer'] == 'Kkma')
    komoran = next(r for r in results if r['analyzer'] == 'Komoran')
    
    # Créer le contenu markdown
    md_content = f"""# Comparaison des 3 Analyseurs NLP Coréens
## {president} - {total_speeches:,} Discours

---

## ⏱️ PERFORMANCES - Temps d'Exécution

| Analyseur | Temps Total | Vitesse | Noms Extraits | Noms Uniques | CPU Moy. | GPU Moy. | Puissance |
|-----------|-------------|---------|---------------|--------------|----------|----------|-----------|
| **Komoran** ⚡ | **{komoran['execution_time_seconds']:.2f}s** | **{komoran['speeches_per_second']:.1f} disc/s** | {komoran['total_nouns']:,} | {komoran['unique_nouns']:,} | {komoran['avg_cpu_percent']:.1f}% | {komoran['avg_gpu_percent']:.1f}% | {komoran['avg_power_watts']:.1f}W |
| **Hannanum** | {hannanum['execution_time_seconds']:.2f}s | {hannanum['speeches_per_second']:.1f} disc/s | {hannanum['total_nouns']:,} | {hannanum['unique_nouns']:,} | {hannanum['avg_cpu_percent']:.1f}% | {hannanum['avg_gpu_percent']:.1f}% | {hannanum['avg_power_watts']:.1f}W |
| **Kkma** 🐌 | {kkma['execution_time_seconds']:.2f}s | {kkma['speeches_per_second']:.1f} disc/s | {kkma['total_nouns']:,} | {kkma['unique_nouns']:,} | {kkma['avg_cpu_percent']:.1f}% | {kkma['avg_gpu_percent']:.1f}% | {kkma['avg_power_watts']:.1f}W |

### 📈 Ratio de Vitesse
- Komoran est **{kkma['execution_time_seconds']/komoran['execution_time_seconds']:.1f}x plus rapide** que Kkma
- Komoran est **{hannanum['execution_time_seconds']/komoran['execution_time_seconds']:.1f}x plus rapide** que Hannanum
- Hannanum est **{kkma['execution_time_seconds']/hannanum['execution_time_seconds']:.1f}x plus rapide** que Kkma

---

## 🏆 TOP 10 MOTS LES PLUS FRÉQUENTS - Comparaison

| Rang | **Komoran** | Fréq. | **Hannanum** | Fréq. | **Kkma** | Fréq. |
|------|-------------|-------|--------------|-------|----------|-------|
"""
    
    # Ajouter le top 10
    for i in range(10):
        k_word = komoran['top_50_words'][i]
        h_word = hannanum['top_50_words'][i]
        kk_word = kkma['top_50_words'][i]
        md_content += f"| **{i+1}** | {k_word['word']} | {k_word['frequency']:,} | {h_word['word']} | {h_word['frequency']:,} | {kk_word['word']} | {kk_word['frequency']:,} |\n"
    
    md_content += f"""
---

## 💡 RECOMMANDATION

**Pour l'analyse de {total_speeches:,} discours de {president.split('(')[0].strip()} :**

### 🥇 Meilleur Choix : **KOMORAN**

**Raisons :**
1. ⚡ **Vitesse** : {komoran['execution_time_seconds']:.2f}s vs {kkma['execution_time_seconds']:.2f}s (Kkma)
2. 📊 **Extraction efficace** : {komoran['total_nouns']:,} noms extraits
3. 🎯 **Normalisation** : {komoran['unique_nouns']:,} noms uniques (meilleure normalisation)
4. 💰 **Meilleur rapport qualité/vitesse**

---

## 📊 TOP 50 MOTS COMPLETS

### Komoran
"""
    
    for word in komoran['top_50_words']:
        md_content += f"{word['rank']:2d}. {word['word']:20s} : {word['frequency']:6,d} fois\n"
    
    md_content += "\n### Hannanum\n"
    for word in hannanum['top_50_words']:
        md_content += f"{word['rank']:2d}. {word['word']:20s} : {word['frequency']:6,d} fois\n"
    
    md_content += "\n### Kkma\n"
    for word in kkma['top_50_words']:
        md_content += f"{word['rank']:2d}. {word['word']:20s} : {word['frequency']:6,d} fois\n"
    
    md_content += f"""
---

## 📁 Fichier de Données

Résultats complets disponibles dans : `{json_file}`
"""
    
    return md_content

# Traiter tous les fichiers JSON
print("🔄 Génération des fichiers markdown de comparaison...")
print("="*80)

json_files = sorted(glob.glob("nlp_analysis_*.json"))
print(f"Fichiers JSON trouvés: {len(json_files)}\n")

for json_file in json_files:
    # Extraire le nom du président
    president_id = json_file.replace("nlp_analysis_", "").replace(".json", "")
    output_file = f"comparison_{president_id}.md"
    
    print(f"📝 {president_id:20s} -> {output_file}")
    
    # Générer le markdown
    md_content = create_comparison_md(json_file)
    
    # Sauvegarder
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

print("\n" + "="*80)
print("✅ GÉNÉRATION TERMINÉE")
print("="*80)
print(f"\n{len(json_files)} fichiers markdown créés:")
print("  • comparison_[president].md")
