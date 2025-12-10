import re
from googletrans import Translator

translator = Translator()

def translate_korean_words(text):
    """Translate Korean words to French and format as 'korean (french)'"""
    words = text.split(' | ')
    translated = []
    
    for word in words:
        try:
            # Translate Korean word to French
            translation = translator.translate(word, src='ko', dest='fr')
            translated.append(f"{word} ({translation.text})")
        except Exception as e:
            print(f"Error translating '{word}': {e}")
            translated.append(f"{word} (?)")
    
    return ' | '.join(translated)

def add_translations_to_tsv(input_file, output_file):
    """Add French translations to Korean words in TSV file"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    in_topics_section = False
    
    for line in lines:
        if line.strip().startswith('Topic_ID'):
            in_topics_section = True
            output_lines.append(line)
        elif in_topics_section and '\t' in line:
            parts = line.strip().split('\t')
            if len(parts) == 3:
                topic_id, nb_para, top_words = parts
                print(f"Translating Topic {topic_id}...")
                translated_words = translate_korean_words(top_words)
                output_lines.append(f"{topic_id}\t{nb_para}\t{translated_words}\n")
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"✓ Translations added to {output_file}")

# Process both files
print("Processing 5-topic file...")
add_translations_to_tsv('lda_analysis_results.tsv', 'lda_analysis_results_translated.tsv')

print("\nProcessing 10-topic file...")
add_translations_to_tsv('lda_analysis_10topics_results.tsv', 'lda_analysis_10topics_results_translated.tsv')

print("\n✓ All translations completed!")
