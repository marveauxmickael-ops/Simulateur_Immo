# 🚀 DÉPLOIEMENT STREAMLIT - Guide complet

## ❌ ERREUR RENCONTRÉE

```
ModuleNotFoundError: ... import matplotlib.pyplot as plt
```

**Cause** : Matplotlib nécessite une configuration spéciale pour Streamlit Cloud (environnement sans interface graphique).

## ✅ SOLUTION APPLIQUÉE

Ajout de cette ligne AVANT l'import de matplotlib :

```python
import matplotlib
matplotlib.use('Agg')  # ← Configuration pour environnement sans GUI
import matplotlib.pyplot as plt
```

---

## 📦 FICHIERS NÉCESSAIRES

### 1️⃣ `estimateur_demo_streamlit.py` 
Le script principal (corrigé pour Streamlit)

### 2️⃣ `requirements.txt`
Les dépendances Python :
```
streamlit>=1.28.0
pandas>=2.0.0
matplotlib>=3.7.0
numpy>=1.24.0
```

---

## 🌐 DÉPLOIEMENT SUR STREAMLIT CLOUD

### Étape 1 : Préparer votre dépôt GitHub

1. Créez un nouveau dépôt GitHub (ex: `simulateur_immo`)
2. Ajoutez ces fichiers :
   - `estimateur_demo_streamlit.py` (renommez en `app.py` ou `streamlit_app.py`)
   - `requirements.txt`

### Étape 2 : Connexion à Streamlit Cloud

1. Allez sur https://share.streamlit.io
2. Connectez-vous avec GitHub
3. Cliquez sur "New app"

### Étape 3 : Configuration

- **Repository** : Sélectionnez `votre-username/simulateur_immo`
- **Branch** : `main`
- **Main file path** : `app.py` (ou le nom de votre fichier)

### Étape 4 : Déploiement

Cliquez sur **Deploy!** et attendez 2-3 minutes.

---

## 🧪 TEST EN LOCAL (avant déploiement)

```bash
# Installation
pip install streamlit pandas matplotlib numpy

# Lancement
streamlit run estimateur_demo_streamlit.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`

---

## 🎨 FONCTIONNALITÉS DE L'APP

### Interface utilisateur
- ✅ Sidebar avec formulaire de saisie
- ✅ Sélection du standing (dropdown)
- ✅ Graphique d'évolution interactif
- ✅ Métriques visuelles (prix min/max/moyen)
- ✅ Résultat en grand avec fourchette de prix

### Données
- 📊 150 transactions simulées sur 5 ans
- 📈 Tendance haussière réaliste
- 🎯 Ajustement par standing (-15% / 0% / +20%)

---

## 🔧 PERSONNALISATION

### Changer les villes disponibles

Modifiez cette ligne (env. ligne 127) :
```python
input_ville = st.text_input("Ville", value="Cavignac")
```

### Modifier les coefficients de standing

Ligne ~149 :
```python
ajustements = {
    Standing.A_RENOVER: 0.85,      # -15%
    Standing.STANDARD: 1.0,         # Prix moyen
    Standing.HAUT_DE_GAMME: 1.20   # +20%
}
```

### Changer les couleurs du graphique

Ligne ~91 :
```python
ax.plot(..., color='#3498db', ...)  # Bleu actuel
```

---

## 🐛 PROBLÈMES COURANTS

### L'app ne démarre pas sur Streamlit Cloud

1. Vérifiez que `requirements.txt` est à la racine du dépôt
2. Vérifiez le nom du fichier principal dans la config
3. Regardez les logs dans "Manage app" → "Logs"

### Erreur "No module named X"

Ajoutez le module manquant dans `requirements.txt`

### Le graphique ne s'affiche pas

Vérifiez la présence de `matplotlib.use('Agg')` AVANT l'import

---

## 📱 STRUCTURE DU PROJET RECOMMANDÉE

```
simulateur_immo/
├── app.py (ou streamlit_app.py)
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml (optionnel, pour le thème)
```

---

## 🎨 EXEMPLE DE CONFIG DE THÈME (optionnel)

Créez `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#3498db"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

---

## ✨ AMÉLIORATIONS FUTURES

- [ ] Connexion à l'API DVF réelle
- [ ] Carte interactive des biens
- [ ] Export PDF du rapport d'estimation
- [ ] Comparaison avec plusieurs villes
- [ ] Historique des estimations

---

**Bon déploiement ! 🚀**

En cas de problème, vérifiez les logs dans Streamlit Cloud → "Manage app" → "View logs"
