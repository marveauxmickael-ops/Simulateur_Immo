import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ← CORRECTION pour Streamlit Cloud
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum
import streamlit as st
from io import StringIO
import numpy as np

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

# --- 2. RÉCUPÉRATION DES DONNÉES DVF RÉELLES ---
def recuperer_transactions_dvf(code_insee: str):
    """
    Récupère les transactions DVF depuis l'API officielle data.gouv.fr
    """
    departement = code_insee[:2]
    url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/2023/communes/{departement}/{code_insee}.csv"
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            # Lecture du CSV
            df = pd.read_csv(StringIO(response.text))
            
            # Filtrage
            df_ventes = df[df['nature_mutation'] == 'Vente']
            df_logements = df_ventes[df_ventes['type_local'].isin(['Maison', 'Appartement'])]
            
            if df_logements.empty:
                return pd.DataFrame(), "Aucune transaction trouvée pour cette commune"
            
            # Sélection des colonnes
            df_final = df_logements[['date_mutation', 'valeur_fonciere', 'surface_reelle_bati']].copy()
            df_final['date_mutation'] = pd.to_datetime(df_final['date_mutation'])
            df_final['valeur_fonciere'] = pd.to_numeric(df_final['valeur_fonciere'], errors='coerce')
            df_final['surface_reelle_bati'] = pd.to_numeric(df_final['surface_reelle_bati'], errors='coerce')
            
            # Filtre surface > 0 et valeurs non nulles
            df_final = df_final.dropna()
            df_final = df_final[df_final['surface_reelle_bati'] > 0]
            
            if df_final.empty:
                return pd.DataFrame(), "Données incomplètes pour cette commune"
            
            return df_final, None
        else:
            return pd.DataFrame(), f"API non disponible (code {response.status_code})"
            
    except Exception as e:
        return pd.DataFrame(), f"Erreur de connexion : {str(e)}"

# --- 3. ANALYSE ET VISUALISATION ---
def analyser_marche(df: pd.DataFrame):
    if df.empty:
        return 0.0, None, None

    # Calcul du prix au m²
    df['prix_m2'] = df['valeur_fonciere'] / df['surface_reelle_bati']
    
    # Suppression des outliers (prix au m² aberrants)
    q1 = df['prix_m2'].quantile(0.05)
    q99 = df['prix_m2'].quantile(0.95)
    df_clean = df[(df['prix_m2'] >= q1) & (df['prix_m2'] <= q99)]
    
    # Moyenne globale
    prix_moyen_global = df_clean['prix_m2'].mean()
    
    # Évolution par année
    df_clean['annee'] = df_clean['date_mutation'].dt.year
    evolution = df_clean.groupby('annee')['prix_m2'].mean().sort_index()
    
    # Statistiques
    stats = {
        'min': int(df_clean['prix_m2'].min()),
        'max': int(df_clean['prix_m2'].max()),
        'moyen': int(prix_moyen_global),
        'mediane': int(df_clean['prix_m2'].median()),
        'nb_transactions': len(df_clean)
    }
    
    # Graphique
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(evolution.index, evolution.values, marker='o', color='#2ecc71', linewidth=2, markersize=8)
    ax.set_title(f"Évolution du prix au m² - Données DVF réelles", fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_ylabel("Prix €/m²", fontsize=11)
    ax.set_xlabel("Année", fontsize=11)
    
    # Ligne de tendance si suffisamment de données
    if len(evolution) > 1:
        z = np.polyfit(evolution.index, evolution.values, 1)
        p = np.poly1d(z)
        ax.plot(evolution.index, p(evolution.index), "r--", alpha=0.5, 
                label=f"Tendance: {'+' if z[0]>0 else ''}{int(z[0])}€/an")
        ax.legend()
    
    plt.tight_layout()
    
    return prix_moyen_global, fig, stats

# --- 4. APPLICATION STREAMLIT ---
def main():
    st.set_page_config(
        page_title="Estimateur Immobilier DVF",
        page_icon="🏡",
        layout="wide"
    )
    
    st.title("🏡 Estimateur Immobilier - Données DVF Réelles")
    st.markdown("*Basé sur les Demandes de Valeurs Foncières (data.gouv.fr)*")
    st.markdown("---")
    
    # Sidebar pour les paramètres
    with st.sidebar:
        st.header("📝 Paramètres du bien")
        
        input_ville = st.text_input("Ville", value="Bordeaux", help="Nom de la ville")
        input_insee = st.text_input(
            "Code INSEE", 
            value="33063", 
            help="Code INSEE de la commune (ex: 33063 pour Bordeaux, 75056 pour Paris)"
        )
        
        st.markdown("**💡 Exemples de codes INSEE:**")
        st.markdown("- Bordeaux: 33063")
        st.markdown("- Paris: 75056")
        st.markdown("- Lyon: 69123")
        st.markdown("- Marseille: 13055")
        
        st.markdown("---")
        
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
        estimer_button = st.button("💰 Estimer avec données réelles", type="primary", use_container_width=True)
    
    # Zone principale
    if estimer_button:
        with st.spinner(f"🔄 Récupération des données DVF pour {input_ville}..."):
            # Création du bien
            mon_bien = BienImmobilier(input_insee, input_ville, input_surface, input_pieces, input_standing)
            
            # Récupération des données RÉELLES
            df_transactions, erreur = recuperer_transactions_dvf(mon_bien.code_insee)
            
            if df_transactions.empty:
                st.error(f"❌ {erreur}")
                st.info("""
                **Suggestions:**
                - Vérifiez que le code INSEE est correct
                - Essayez une ville plus grande (ex: 33063 pour Bordeaux)
                - Certaines petites communes n'ont pas assez de transactions
                """)
                return
            
            # Analyse
            prix_moyen_m2, fig, stats = analyser_marche(df_transactions)
            
            if prix_moyen_m2 == 0:
                st.error("❌ Impossible d'analyser les données de cette commune")
                return
            
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
            st.success(f"✅ {stats['nb_transactions']} transactions DVF analysées pour {mon_bien.ville}")
            
            # Colonnes pour l'affichage
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 Statistiques du marché (DVF)")
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Prix minimum", f"{stats['min']:,} €/m²".replace(',', ' '))
                    st.metric("Prix moyen", f"{stats['moyen']:,} €/m²".replace(',', ' '))
                with metric_col2:
                    st.metric("Prix maximum", f"{stats['max']:,} €/m²".replace(',', ' '))
                    st.metric("Médiane", f"{stats['mediane']:,} €/m²".replace(',', ' '))
                
                st.info(f"📈 **{stats['nb_transactions']}** transactions immobilières analysées")
                
                st.markdown("---")
                
                st.subheader("🏠 Détails de l'estimation")
                st.write(f"**Localisation:** {mon_bien.ville} ({mon_bien.code_insee})")
                st.write(f"**Surface:** {mon_bien.surface_habitable} m²")
                st.write(f"**Pièces:** {mon_bien.nombre_pieces}")
                st.write(f"**Standing:** {mon_bien.standing.value}")
                st.write(f"**Coefficient appliqué:** {coefficient}")
            
            with col2:
                st.subheader("📈 Évolution des prix (DVF)")
                st.pyplot(fig)
                st.caption("Graphique basé sur les transactions réelles enregistrées")
            
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
            st.success("""
            ✅ **Estimation basée sur des données officielles DVF**
            
            Les Demandes de Valeurs Foncières (DVF) sont les données officielles de l'administration fiscale 
            concernant les transactions immobilières en France.
            """)
            
            # Détails techniques (repliable)
            with st.expander("🔍 Détails techniques"):
                st.write(f"**Source des données:** API data.gouv.fr")
                st.write(f"**Année des données:** 2023")
                st.write(f"**Nombre de transactions brutes:** {stats['nb_transactions']}")
                st.write(f"**Filtres appliqués:** Ventes uniquement, Maisons et Appartements, Surface > 0m²")
                st.write(f"**Outliers exclus:** 5% prix les plus bas et 5% prix les plus élevés")
    
    else:
        # Message d'accueil
        st.info("👈 Configurez les paramètres dans la barre latérale et cliquez sur **Estimer avec données réelles**")
        
        # Guide d'utilisation
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Comment utiliser cet outil ?
            
            1. **Saisissez** le code INSEE de la commune
            2. **Renseignez** les caractéristiques du bien
            3. **Choisissez** le standing du bien
            4. **Cliquez** sur "Estimer avec données réelles"
            5. **Consultez** les résultats issus des transactions DVF
            """)
        
        with col2:
            st.markdown("""
            ### 📌 À propos des données DVF
            
            - ✅ Données **officielles** de l'administration fiscale
            - ✅ Transactions **réelles** enregistrées
            - ✅ Mise à jour **régulière** par data.gouv.fr
            - ⚠️ Disponibles uniquement pour les communes avec suffisamment de transactions
            - ⚠️ Données 2023 (dernière année complète disponible)
            """)
        
        st.markdown("---")
        st.warning("""
        ⚠️ **Note importante:** L'API peut ne pas fonctionner pour toutes les communes, 
        notamment les petites communes rurales avec peu de transactions. 
        Dans ce cas, essayez avec une ville plus grande.
        """)

if __name__ == "__main__":
    main()
