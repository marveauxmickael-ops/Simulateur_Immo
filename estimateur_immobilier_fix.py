import requests
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# --- 1. MODÉLISATION (US-01) ---
class Standing(Enum):
    A_RENOVER = "À rénover"
    STANDARD = "Standard"
    HAUT_DE_GAMME = "Haut de gamme"

@dataclass
class BienImmobilier:
    code_insee: str
    ville: str
    surface_habitable: float
    nombre_pieces: int
    standing: Standing

# --- 2. RÉCUPÉRATION DES DONNÉES (CORRIGÉ) ---
def recuperer_transactions_dvf(code_insee: str):
    print(f"🔄 Connexion à la base DVF pour le code INSEE {code_insee}...")
    
    # OPTION 1 : API officielle data.gouv.fr (CSV)
    # Format : https://files.data.gouv.fr/geo-dvf/latest/csv/ANNEE/communes/DEP/CODINSEE.csv
    departement = code_insee[:2]
    url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/2023/communes/{departement}/{code_insee}.csv"
    
    try:
        print(f"🌐 URL : {url}")
        response = requests.get(url, timeout=15)
        print(f"DEBUG: Statut HTTP : {response.status_code}")
        
        if response.status_code == 200:
            # Lecture du CSV directement
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            print(f"DEBUG: Nombre de lignes brutes : {len(df)}")
            print(f"DEBUG: Colonnes disponibles : {list(df.columns)[:10]}...")  # Affiche 10 premières
            
            # Filtrage
            df_ventes = df[df['nature_mutation'] == 'Vente']
            print(f"DEBUG: Après filtre 'Vente' : {len(df_ventes)} lignes")
            
            df_logements = df_ventes[df_ventes['type_local'].isin(['Maison', 'Appartement'])]
            print(f"DEBUG: Après filtre 'Maison/Appartement' : {len(df_logements)} lignes")
            
            # Sélection des colonnes
            df_final = df_logements[['date_mutation', 'valeur_fonciere', 'surface_reelle_bati']].copy()
            df_final['date_mutation'] = pd.to_datetime(df_final['date_mutation'])
            df_final['valeur_fonciere'] = pd.to_numeric(df_final['valeur_fonciere'])
            df_final['surface_reelle_bati'] = pd.to_numeric(df_final['surface_reelle_bati'])
            
            # Filtre surface > 0
            df_final = df_final[df_final['surface_reelle_bati'] > 0]
            print(f"✅ DEBUG: Données finales : {len(df_final)} lignes\n")
            
            return df_final
        else:
            print(f"⚠️ Erreur HTTP {response.status_code}")
            print("💡 TIP: Vérifiez que le code INSEE existe et que data.gouv.fr a des données pour 2023")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erreur technique : {e}")
        return pd.DataFrame()

# --- 3. ANALYSE ET VISUALISATION (US-03) ---
def analyser_marche(df: pd.DataFrame):
    if df.empty:
        return 0.0

    # Calcul du prix au m²
    df['prix_m2'] = df['valeur_fonciere'] / df['surface_reelle_bati']
    
    # Moyenne globale
    prix_moyen_global = df['prix_m2'].mean()
    
    # Évolution par année
    df['annee'] = df['date_mutation'].dt.year
    evolution = df.groupby('annee')['prix_m2'].mean().sort_index()
    
    # Graphique
    plt.figure(figsize=(10, 5))
    plt.plot(evolution.index, evolution.values, marker='o', color='#3498db', linewidth=2)
    plt.title(f"Évolution du prix au m² (Moyenne : {int(prix_moyen_global)}€)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.ylabel("Prix €/m²")
    plt.xlabel("Année")
    
    print("📊 Génération du graphique d'évolution...")
    plt.savefig('evolution_prix_m2.png', dpi=100, bbox_inches='tight')
    print("✅ Graphique sauvegardé : evolution_prix_m2.png")
    plt.close()
    
    return prix_moyen_global

# --- 4. PROGRAMME PRINCIPAL ---
def main():
    print("=== 🏡 ESTIMATEUR IMMOBILIER (MVP) ===\n")
    
    # Paramètres du bien
    input_ville = "Cavignac"
    input_insee = "33114"
    input_surface = 75.0
    input_pieces = 3
    input_standing = Standing.STANDARD

    mon_bien = BienImmobilier(input_insee, input_ville, input_surface, input_pieces, input_standing)
    
    print(f"1️⃣ Bien identifié : {mon_bien.ville} | {mon_bien.surface_habitable}m² | {mon_bien.standing.value}\n")

    # Récupération des données
    df_transactions = recuperer_transactions_dvf(mon_bien.code_insee)
    
    if df_transactions.empty:
        print("\n❌ Pas de données disponibles.")
        print("💡 Essayez avec un code INSEE d'une ville plus grande (ex: 33063 pour Bordeaux)")
        return

    # Analyse
    prix_moyen_m2 = analyser_marche(df_transactions)

    # Estimation finale
    estimation_brute = prix_moyen_m2 * mon_bien.surface_habitable
    
    print("\n" + "="*50)
    print(f"💰 RÉSULTAT DE L'ESTIMATION")
    print(f"Prix moyen secteur : {int(prix_moyen_m2):,} €/m²")
    print(f"Valeur estimée     : {int(estimation_brute):,} €")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
