#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse NLP Complète - TOUS LES PRÉSIDENTS
3 Analyseurs (Hannanum, Kkma, Komoran) avec monitoring CPU/GPU/Watts
"""

import json
import time
import psutil
import subprocess
from collections import Counter
from konlpy.tag import Hannanum, Kkma, Komoran

# Stop words enrichis
KOREAN_STOPWORDS = {
    '이', '가', '을', '를', '은', '는', '에', '에서', '의', '와', '과', '로', '으로',
    '도', '만', '부터', '까지', '에게', '한테', '께', '보다', '처럼', '같이',
    '나', '너', '저', '우리', '그', '이', '저', '여기', '거기', '저기',
    '이것', '그것', '저것', '누구', '무엇', '어디', '언제', '어떻게',
    '하다', '되다', '있다', '없다', '이다', '아니다',
    '지금', '오늘', '어제', '내일', '여기', '거기', '저기',
    '그리고', '그러나', '하지만', '또', '또한', '및',
    '일', '이', '삼', '사', '오', '육', '칠', '팔', '구', '십',
    '등', '것', '수', '때', '년', '월', '일', '중', '간', '말', '점', '바',
    # Métadonnées
    '담화', '박사', '대통령이승만', '대통령이승만박사', '대통령이승만박사담화',
    '공보처', '공보실', '편', '집', '훈화록', '이대통령', '중앙문화협회'
}

def get_gpu_stats():
    """Récupère les stats GPU via nvidia-smi"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,power.draw', 
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            gpu_util, mem_used, power = result.stdout.strip().split(',')
            return {
                'gpu_utilization': float(gpu_util),
                'memory_used_mb': float(mem_used),
                'power_watts': float(power)
            }
    except:
        pass
    return {'gpu_utilization': 0, 'memory_used_mb': 0, 'power_watts': 0}

def analyze_president(president_name, file_path, analyzers):
    """Analyse un président avec les 3 analyseurs"""
    print(f"\n{'='*80}")
    print(f"📖 PRÉSIDENT: {president_name}")
    print(f"{'='*80}")
    
    # Charger les discours
    with open(file_path, 'r', encoding='utf-8') as f:
        speeches = json.load(f)
    
    total_speeches = len(speeches)
    print(f"   ✓ {total_speeches:,} discours chargés\n")
    
    # Préparer les textes
    texts = [" ".join(speech["paragraphs"]) for speech in speeches]
    
    results = []
    
    for analyzer_name, analyzer in analyzers.items():
        print(f"\n🔍 Analyse avec {analyzer_name}...")
        
        # Monitoring initial
        cpu_samples = []
        gpu_samples = []
        process = psutil.Process()
        
        start_time = time.time()
        all_nouns = []
        
        for idx, text in enumerate(texts, 1):
            if idx % 100 == 0:
                # Échantillonner CPU/GPU
                cpu_samples.append(process.cpu_percent(interval=0.1))
                gpu_samples.append(get_gpu_stats())
                
                elapsed = time.time() - start_time
                print(f"  {idx}/{total_speeches} discours ({elapsed:.1f}s)")
            
            nouns = analyzer.nouns(text)
            nouns_filtered = [w for w in nouns if w not in KOREAN_STOPWORDS 
                            and len(w) > 1 and not w.isdigit()]
            all_nouns.extend(nouns_filtered)
        
        total_time = time.time() - start_time
        
        # Stats finales
        word_freq = Counter(all_nouns)
        top_50 = word_freq.most_common(50)
        
        # Moyennes CPU/GPU
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        avg_gpu_util = sum(s['gpu_utilization'] for s in gpu_samples) / len(gpu_samples) if gpu_samples else 0
        avg_power = sum(s['power_watts'] for s in gpu_samples) / len(gpu_samples) if gpu_samples else 0
        
        print(f"   ✓ Terminé en {total_time:.2f}s")
        print(f"   CPU moyen: {avg_cpu:.1f}%")
        print(f"   GPU moyen: {avg_gpu_util:.1f}%")
        print(f"   Puissance: {avg_power:.1f}W")
        
        results.append({
            'analyzer': analyzer_name,
            'execution_time_seconds': round(total_time, 2),
            'speeches_per_second': round(total_speeches/total_time, 2),
            'total_nouns': len(all_nouns),
            'unique_nouns': len(word_freq),
            'avg_cpu_percent': round(avg_cpu, 1),
            'avg_gpu_percent': round(avg_gpu_util, 1),
            'avg_power_watts': round(avg_power, 1),
            'top_50_words': [{'rank': i+1, 'word': w, 'frequency': c} 
                           for i, (w, c) in enumerate(top_50)]
        })
    
    return {
        'president': president_name,
        'total_speeches': total_speeches,
        'results': results
    }

# Liste des présidents
PRESIDENTS = [
    ('Choi_Kyu_Hah', 'Choi Kyu Hah (최규하)'),
    ('Chun_Doo_Hwan', 'Chun Doo Hwan (전두환)'),
    ('Kim_Dae_Jung', 'Kim Dae Jung (김대중)'),
    ('Kim_Young_Sam', 'Kim Young Sam (김영삼)'),
    ('Lee_Myung_Bak', 'Lee Myung Bak (이명박)'),
    ('Lee_Seung_Man', 'Lee Seung Man (이승만)'),
    ('Moon_Jae_In', 'Moon Jae In (문재인)'),
    ('Park_Chung_Hee', 'Park Chung Hee (박정희)'),
    ('Park_Geun_Hye', 'Park Geun Hye (박근혜)'),
    ('Roh_Moo_Hyun', 'Roh Moo Hyun (노무현)'),
    ('Roh_Tae_Woo', 'Roh Tae Woo (노태우)'),
    ('Yun_Bo_Seon', 'Yun Bo Seon (윤보선)')
]

print("="*80, flush=True)
print("🇰🇷 ANALYSE NLP - TOUS LES PRÉSIDENTS CORÉENS", flush=True)
print("="*80, flush=True)
print(f"\nNombre de présidents: {len(PRESIDENTS)}", flush=True)
print("Analyseurs: Hannanum, Kkma, Komoran", flush=True)
print("Monitoring: CPU, GPU, Watts\n", flush=True)

# Initialiser les analyseurs
print("🔧 Initialisation des analyseurs...", flush=True)
analyzers = {
    'Hannanum': Hannanum(),
    'Kkma': Kkma(),
    'Komoran': Komoran()
}
print("   ✓ Tous prêts\n", flush=True)

# Analyser chaque président
all_results = []

for file_id, president_name in PRESIDENTS:
    file_path = f"president_texts_{file_id}.json"
    
    try:
        result = analyze_president(president_name, file_path, analyzers)
        all_results.append(result)
        
        # Sauvegarder individuellement
        output_file = f"nlp_analysis_{file_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Sauvegardé: {output_file}")
        
    except FileNotFoundError:
        print(f"⚠️  Fichier non trouvé: {file_path}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

# Résumé global
print("\n" + "="*80)
print("📊 RÉSUMÉ GLOBAL")
print("="*80)

for result in all_results:
    print(f"\n{result['president']} ({result['total_speeches']} discours):")
    for r in result['results']:
        print(f"  {r['analyzer']:10s}: {r['execution_time_seconds']:6.1f}s | "
              f"CPU {r['avg_cpu_percent']:4.1f}% | "
              f"GPU {r['avg_gpu_percent']:4.1f}% | "
              f"{r['avg_power_watts']:5.1f}W")

# Sauvegarder résumé global
with open('all_presidents_summary.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("✅ ANALYSE COMPLÈTE TERMINÉE")
print("="*80)
print(f"\nFichiers créés:")
print(f"  • nlp_analysis_[president].json (12 fichiers)")
print(f"  • all_presidents_summary.json (résumé global)")
