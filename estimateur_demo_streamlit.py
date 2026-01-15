import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ← CORRECTION CRITIQUE pour Streamlit
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

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
    
    return df

# --- 3. ANALYSE ET VISUALISATION ---
def analyser_marche(df: pd.DataFrame):
    if df.empty:
        return 0.0, None

    # Calcul du prix au m²
    df['prix_m2'] = df['valeur_fonciere'] / df['surface_reelle_bati']
    
    # Moyenne globale
    prix_moyen_global = df['prix_m2'].mean()
    
    # Évolution par année
    df['annee'] = df['date_mutation'].dt.year
    evolution = df.groupby('annee')['prix_m2'].mean().sort_index()
    
    # Statistiques
    stats = {
        'min': int(df['prix_m2'].min()),
        'max': int(df['prix_m2'].max()),
        'moyen': int(prix_moyen_global),
        'mediane': int(df['prix_m2'].median())
    }
    
    # Graphique
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(evolution.index, evolution.values, marker='o', color='#3498db', linewidth=2, markersize=8)
    ax.set_title(f"Évolution du prix au m² - {df['annee'].min()} à {df['annee'].max()}", fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_ylabel("Prix €/m²", fontsize=11)
    ax.set_xlabel("Année", fontsize=11)
    
    # Ligne de tendance
    z = np.polyfit(evolution.index, evolution.values, 1)
    p = np.poly1d(z)
    ax.plot(evolution.index, p(evolution.index), "r--", alpha=0.5, label=f"Tendance: +{int(z[0])}€/an")
    ax.legend()
    
    plt.tight_layout()
    
    return prix_moyen_global, fig, stats

# --- 4. APPLICATION STREAMLIT ---
def main():
    st.set_page_config(
        page_title="Estimateur Immobilier",
        page_icon="🏡",
        layout="wide"
    )
    
    st.title("🏡 Estimateur Immobilier")
    st.markdown("---")
    
    # Sidebar pour les paramètres
    with st.sidebar:
        st.header("📝 Paramètres du bien")
        
        input_ville = st.text_input("Ville", value="Cavignac")
        input_insee = st.text_input("Code INSEE", value="33114")
        input_surface = st.number_input("Surface (m²)", min_value=10.0, max_value=500.0, value=75.0, step=5.0)
        input_pieces = st.number_input("Nombre de pièces", min_value=1, max_value=20, value=3, step=1)
        
        input_standing_label = st.selectbox(
            "Standing",
            ["Standard", "À rénover", "Haut de gamme"]
        )
        
        # Mapping vers l'enum
        standing_map = {
            "Standard": Standing.STANDARD,
            "À rénover": Standing.A_RENOVER,
            "Haut de gamme": Standing.HAUT_DE_GAMME
        }
        input_standing = standing_map[input_standing_label]
        
        st.markdown("---")
        estimer_button = st.button("💰 Estimer", type="primary", use_container_width=True)
    
    # Zone principale
    if estimer_button:
        with st.spinner("🔄 Analyse en cours..."):
            # Création du bien
            mon_bien = BienImmobilier(input_insee, input_ville, input_surface, input_pieces, input_standing)
            
            # Récupération des données
            df_transactions = generer_donnees_demo(mon_bien.code_insee)
            
            if df_transactions.empty:
                st.error("❌ Pas de données disponibles pour cette commune.")
                return
            
            # Analyse
            prix_moyen_m2, fig, stats = analyser_marche(df_transactions)
            
            # Ajustement selon le standing
            ajustements = {
                Standing.A_RENOVER: 0.85,
                Standing.STANDARD: 1.0,
                Standing.HAUT_DE_GAMME: 1.20
            }
            
            coefficient = ajustements[mon_bien.standing]
            prix_ajuste_m2 = prix_moyen_m2 * coefficient
            estimation_finale = prix_ajuste_m2 * mon_bien.surface_habitable
            
            # Affichage des résultats
            st.success(f"✅ Estimation réalisée pour {mon_bien.ville}")
            
            # Colonnes pour l'affichage
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 Statistiques du marché")
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Prix minimum", f"{stats['min']:,} €/m²".replace(',', ' '))
                    st.metric("Prix moyen", f"{stats['moyen']:,} €/m²".replace(',', ' '))
                with metric_col2:
                    st.metric("Prix maximum", f"{stats['max']:,} €/m²".replace(',', ' '))
                    st.metric("Médiane", f"{stats['mediane']:,} €/m²".replace(',', ' '))
                
                st.markdown("---")
                
                st.subheader("🏠 Détails de l'estimation")
                st.write(f"**Localisation:** {mon_bien.ville} ({mon_bien.code_insee})")
                st.write(f"**Surface:** {mon_bien.surface_habitable} m²")
                st.write(f"**Pièces:** {mon_bien.nombre_pieces}")
                st.write(f"**Standing:** {mon_bien.standing.value}")
                st.write(f"**Coefficient appliqué:** {coefficient}")
            
            with col2:
                st.subheader("📈 Évolution des prix")
                st.pyplot(fig)
            
            # Résultat final en grand
            st.markdown("---")
            st.markdown("## 💰 RÉSULTAT DE L'ESTIMATION")
            
            result_col1, result_col2, result_col3 = st.columns(3)
            
            with result_col1:
                st.metric(
                    "Fourchette basse (-5%)",
                    f"{int(estimation_finale * 0.95):,} €".replace(',', ' ')
                )
            
            with result_col2:
                st.metric(
                    "VALEUR ESTIMÉE",
                    f"{int(estimation_finale):,} €".replace(',', ' '),
                    delta=None
                )
            
            with result_col3:
                st.metric(
                    "Fourchette haute (+5%)",
                    f"{int(estimation_finale * 1.05):,} €".replace(',', ' ')
                )
            
            # Note d'information
            st.info("ℹ️ Cette estimation est basée sur des données simulées à des fins de démonstration. En production, elle utiliserait les données réelles de DVF (Demandes de Valeurs Foncières).")
    
    else:
        # Message d'accueil
        st.info("👈 Configurez les paramètres dans la barre latérale et cliquez sur **Estimer**")
        
        # Image ou illustration d'accueil
        st.markdown("""
        ### 🎯 Comment utiliser cet outil ?
        
        1. **Renseignez** les informations du bien dans la barre latérale
        2. **Choisissez** le standing du bien
        3. **Cliquez** sur le bouton "Estimer"
        4. **Consultez** les résultats et le graphique d'évolution
        
        ### 📌 Informations importantes
        
        - Les estimations sont basées sur les transactions immobilières récentes
        - Le standing du bien influence le coefficient appliqué au prix moyen
        - La fourchette de prix vous donne une marge de sécurité de ±5%
        """)

if __name__ == "__main__":
    main()
