#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilitaire pour lire les exports CSV de TXM dans Pandas
Supporte : Lexiques, Spécificités, Concordances
"""

import pandas as pd
import io
import os

def read_txm_csv(file_path):
    """
    Lit un fichier CSV exporté de TXM et le retourne sous forme de DataFrame Pandas.
    Gère automatiquement les délimiteurs et l'encodage.
    """
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        return None

    # Tentative de détection du délimiteur et de l'encodage
    # TXM utilise souvent le point-virgule ou la tabulation
    delimiters = [';', '\t', ',']
    encodings = ['utf-8', 'latin-1', 'utf-16']
    
    df = None
    for encoding in encodings:
        for sep in delimiters:
            try:
                # Lecture d'un échantillon pour vérifier si le séparateur est correct
                temp_df = pd.read_csv(file_path, sep=sep, encoding=encoding, nrows=5)
                if len(temp_df.columns) > 1:
                    # Si on a plusieurs colonnes, c'est probablement le bon séparateur
                    df = pd.read_csv(file_path, sep=sep, encoding=encoding)
                    
                    # Nettoyage des noms de colonnes (TXM ajoute parfois des guillemets)
                    df.columns = [c.strip('"').strip("'") for c in df.columns]
                    
                    # Nettoyage des données textuelles
                    df = df.apply(lambda x: x.str.strip('"').str.strip("'") if x.dtype == "object" else x)
                    
                    print(f"✅ Fichier lu avec succès (sep='{sep}', encoding='{encoding}')")
                    return df
            except Exception:
                continue
    
    print(f"❌ Impossible de lire le fichier {file_path} avec les paramètres standards.")
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Charge un export CSV de TXM dans un DataFrame Pandas")
    parser.add_argument("file", help="Chemin vers le fichier CSV exporté de TXM")
    parser.add_argument("--head", type=int, default=10, help="Nombre de lignes à afficher")
    args = parser.parse_args()

    df = read_txm_csv(args.file)
    if df is not None:
        print("\n📊 Aperçu des données :")
        print(df.head(args.head))
        print(f"\nDimensions : {df.shape}")
        
        # Exemple d'analyse rapide selon les colonnes présentes
        if 'freq' in df.columns or 'f' in df.columns:
            print("\n💡 Type détecté : Index / Lexique")
        elif 'L' in df.columns and 'Pivot' in df.columns:
            print("\n💡 Type détecté : Concordance")
        elif any('score' in c.lower() for c in df.columns):
            print("\n💡 Type détecté : Spécificités")

if __name__ == "__main__":
    main()
