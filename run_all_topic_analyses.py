#!/usr/bin/env python3
"""
Master script to run all topic modeling analyses (LDA and LSA) on presidential speeches
Compares CPU vs GPU performance for LSA
"""

import subprocess
import time
import json
import os
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and capture its execution details"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ['python3', script_name],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        execution_time = time.time() - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        
        return {
            'script': script_name,
            'description': description,
            'success': success,
            'execution_time': execution_time,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        print(f"⚠️  Script timed out after {execution_time:.2f}s")
        return {
            'script': script_name,
            'description': description,
            'success': False,
            'execution_time': execution_time,
            'returncode': -1,
            'error': 'Timeout'
        }
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Error running script: {e}")
        return {
            'script': script_name,
            'description': description,
            'success': False,
            'execution_time': execution_time,
            'returncode': -1,
            'error': str(e)
        }

def main():
    """Run all topic modeling analyses"""
    
    print("="*80)
    print("TOPIC MODELING ANALYSIS PIPELINE")
    print("Analyzing all presidential speeches with LDA and LSA (CPU & GPU)")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Define all analyses to run
    analyses = [
        {
            'script': 'analyse_lda_15topics.py',
            'description': 'LDA Topic Modeling (15 topics) - CPU'
        },
        {
            'script': 'analyse_lsa_cpu.py',
            'description': 'LSA + K-means (15 topics) - CPU'
        },
        {
            'script': 'analyse_lsa_gpu.py',
            'description': 'LSA + K-means (15 topics) - GPU'
        }
    ]
    
    # Check that all scripts exist
    missing_scripts = []
    for analysis in analyses:
        if not os.path.exists(analysis['script']):
            missing_scripts.append(analysis['script'])
    
    if missing_scripts:
        print("\n❌ ERROR: The following scripts are missing:")
        for script in missing_scripts:
            print(f"   - {script}")
        return
    
    # Run all analyses
    results = []
    total_start = time.time()
    
    for analysis in analyses:
        result = run_script(analysis['script'], analysis['description'])
        results.append(result)
        
        if result['success']:
            print(f"\n✓ {analysis['description']} completed in {result['execution_time']:.2f}s")
        else:
            print(f"\n✗ {analysis['description']} failed after {result['execution_time']:.2f}s")
    
    total_time = time.time() - total_start
    
    # Generate summary report
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\nTotal analyses run: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total execution time: {total_time:.2f}s ({total_time/60:.2f} minutes)")
    
    print("\n" + "-"*80)
    print("Individual Results:")
    print("-"*80)
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['description']}: {result['execution_time']:.2f}s")
    
    # Save detailed results to JSON
    results_file = f"topic_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_time': total_time,
            'successful': successful,
            'failed': failed,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Detailed results saved to: {results_file}")
    
    # Generate comparison table from TSV files
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)
    
    try:
        generate_comparison_table()
    except Exception as e:
        print(f"⚠️  Could not generate comparison table: {e}")
    
    print("\n" + "="*80)
    print(f"Pipeline completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def generate_comparison_table():
    """Generate a comparison table from the TSV result files"""
    
    files = [
        ('lda_15topics_results.tsv', 'LDA (CPU)'),
        ('lsa_cpu_15topics_results.tsv', 'LSA CPU'),
        ('lsa_gpu_15topics_results.tsv', 'LSA GPU')
    ]
    
    comparison_data = {}
    
    for filename, label in files:
        if not os.path.exists(filename):
            print(f"⚠️  File not found: {filename}")
            continue
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        data = {}
        for line in lines:
            if '\t' in line and not line.startswith('Topic_ID'):
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    key, value = parts
                    data[key] = value
        
        comparison_data[label] = data
    
    if not comparison_data:
        print("No data files found for comparison")
        return
    
    # Print comparison table
    print("\n")
    print(f"{'Metric':<30} {'LDA (CPU)':<15} {'LSA CPU':<15} {'LSA GPU':<15}")
    print("-" * 80)
    
    metrics = [
        'Nb_Discours',
        'Nb_Presidents', 
        'Nb_Paragraphs',
        'Nb_Topics',
        'Execution_Time_Sec',
        'CPU_Usage_Percent',
        'Memory_Usage_Percent',
        'GPU_Usage_Percent',
        'GPU_Power_Watts'
    ]
    
    for metric in metrics:
        row = f"{metric:<30}"
        for label in ['LDA (CPU)', 'LSA CPU', 'LSA GPU']:
            value = comparison_data.get(label, {}).get(metric, 'N/A')
            row += f" {value:<15}"
        print(row)
    
    # Save comparison to markdown file
    md_file = 'topic_modeling_comparison.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Topic Modeling Performance Comparison\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Performance Metrics\n\n")
        f.write("| Metric | LDA (CPU) | LSA CPU | LSA GPU |\n")
        f.write("|--------|-----------|---------|----------|\n")
        
        for metric in metrics:
            row = f"| {metric} |"
            for label in ['LDA (CPU)', 'LSA CPU', 'LSA GPU']:
                value = comparison_data.get(label, {}).get(metric, 'N/A')
                row += f" {value} |"
            f.write(row + "\n")
        
        f.write("\n## Analysis Details\n\n")
        f.write("- **LDA**: Latent Dirichlet Allocation using sklearn (CPU-based)\n")
        f.write("- **LSA CPU**: Latent Semantic Analysis with K-means clustering using sklearn (CPU)\n")
        f.write("- **LSA GPU**: Latent Semantic Analysis with K-means clustering using PyTorch (GPU-accelerated)\n\n")
        f.write("All analyses performed on the complete corpus of presidential speeches.\n")
    
    print(f"\n✓ Comparison saved to: {md_file}")

if __name__ == "__main__":
    main()
