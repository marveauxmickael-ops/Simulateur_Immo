import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime, timedelta

# --- 1. MODÉLISATION ---
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

# --- 2. DONNÉES SIMULÉES (pour démo) ---
def generer_donnees_demo(code_insee: str):
    """
    Génère des données réalistes pour la démonstration
    En production, cette fonction serait remplacée par l'API DVF
    """
    print(f"🔄 Génération de données de démonstration pour {code_insee}...")
    
    np.random.seed(42)  # Pour reproductibilité
    
    # Générer 150 transactions sur 5 ans
    n_transactions = 150
    dates = [datetime(2019, 1, 1) + timedelta(days=np.random.randint(0, 1825)) for _ in range(n_transactions)]
    
    # Prix au m² avec tendance haussière : base 2000€/m² en 2019 → 2500€/m² en 2024
    prix_m2_base = np.array([2000 + (d.year - 2019) * 100 for d in dates])
    prix_m2 = prix_m2_base + np.random.normal(0, 200, n_transactions)
    
    # Surfaces entre 30 et 150 m²
    surfaces = np.random.uniform(30, 150, n_transactions)
    
    # Valeurs foncières
    valeurs = prix_m2 * surfaces
    
    df = pd.DataFrame({
        'date_mutation': dates,
        'valeur_fonciere': valeurs,
        'surface_reelle_bati': surfaces
    })
    
    print(f"✅ {len(df)} transactions générées (données de démonstration)")
    return df

# --- 3. ANALYSE ET VISUALISATION ---
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
    
    # Statistiques
    print("\n📊 STATISTIQUES DU MARCHÉ")
    print(f"Prix min  : {int(df['prix_m2'].min())} €/m²")
    print(f"Prix max  : {int(df['prix_m2'].max())} €/m²")
    print(f"Prix moyen: {int(prix_moyen_global)} €/m²")
    print(f"Médiane   : {int(df['prix_m2'].median())} €/m²")
    
    # Graphique
    plt.figure(figsize=(10, 5))
    plt.plot(evolution.index, evolution.values, marker='o', color='#3498db', linewidth=2, markersize=8)
    plt.title(f"Évolution du prix au m² - {df['annee'].min()} à {df['annee'].max()}", fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.ylabel("Prix €/m²", fontsize=11)
    plt.xlabel("Année", fontsize=11)
    
    # Ajout de la ligne de tendance
    z = np.polyfit(evolution.index, evolution.values, 1)
    p = np.poly1d(z)
    plt.plot(evolution.index, p(evolution.index), "r--", alpha=0.5, label=f"Tendance: +{int(z[0])}€/an")
    plt.legend()
    
    plt.savefig('evolution_prix_m2.png', dpi=120, bbox_inches='tight')
    print("\n✅ Graphique sauvegardé : evolution_prix_m2.png")
    plt.close()
    
    return prix_moyen_global

# --- 4. PROGRAMME PRINCIPAL ---
def main():
    print("="*60)
    print("🏡 ESTIMATEUR IMMOBILIER - MODE DÉMONSTRATION")
    print("="*60)
    print("⚠️  Utilisation de données simulées (API DVF non accessible)")
    print("="*60 + "\n")
    
    # Paramètres du bien
    input_ville = "Cavignac"
    input_insee = "33114"
    input_surface = 75.0
    input_pieces = 3
    input_standing = Standing.STANDARD

    mon_bien = BienImmobilier(input_insee, input_ville, input_surface, input_pieces, input_standing)
    
    print(f"1️⃣ BIEN À ESTIMER")
    print(f"   Localisation : {mon_bien.ville} ({mon_bien.code_insee})")
    print(f"   Surface      : {mon_bien.surface_habitable} m²")
    print(f"   Pièces       : {mon_bien.nombre_pieces}")
    print(f"   Standing     : {mon_bien.standing.value}")
    
    # Récupération des données (simulées pour la démo)
    df_transactions = generer_donnees_demo(mon_bien.code_insee)
    
    if df_transactions.empty:
        print("\n❌ Pas de données disponibles.")
        return

    # Analyse
    prix_moyen_m2 = analyser_marche(df_transactions)

    # Ajustement selon le standing
    ajustements = {
        Standing.A_RENOVER: 0.85,
        Standing.STANDARD: 1.0,
        Standing.HAUT_DE_GAMME: 1.20
    }
    
    coefficient = ajustements[mon_bien.standing]
    prix_ajuste_m2 = prix_moyen_m2 * coefficient
    estimation_finale = prix_ajuste_m2 * mon_bien.surface_habitable
    
    # Résultat
    print("\n" + "="*60)
    print("💰 RÉSULTAT DE L'ESTIMATION")
    print("="*60)
    print(f"Prix moyen secteur      : {int(prix_moyen_m2):,} €/m²".replace(',', ' '))
    print(f"Coefficient standing    : {coefficient} ({mon_bien.standing.value})")
    print(f"Prix ajusté             : {int(prix_ajuste_m2):,} €/m²".replace(',', ' '))
    print(f"\n🏠 VALEUR ESTIMÉE        : {int(estimation_finale):,} €".replace(',', ' '))
    print(f"   Fourchette basse (-5%): {int(estimation_finale * 0.95):,} €".replace(',', ' '))
    print(f"   Fourchette haute (+5%): {int(estimation_finale * 1.05):,} €".replace(',', ' '))
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
