# 🏡 Estimateur Immobilier - Versions Streamlit

Ce dépôt contient **deux versions** de l'estimateur immobilier pour Streamlit :

---

## 📦 FICHIERS FOURNIS

### Version 1 : Démonstration (données simulées)
- **Fichier:** `estimateur_demo_streamlit.py`
- **Données:** Simulées (150 transactions réalistes)
- **Avantages:** 
  - ✅ Fonctionne toujours (pas de dépendance réseau)
  - ✅ Rapide et fiable
  - ✅ Idéal pour tester l'interface
- **Inconvénients:**
  - ❌ Données fictives

### Version 2 : Production (données DVF réelles)
- **Fichier:** `estimateur_immobilier_streamlit.py`
- **Données:** API officielle DVF (data.gouv.fr)
- **Avantages:**
  - ✅ Données **officielles** de l'administration fiscale
  - ✅ Transactions **réelles**
  - ✅ Estimation précise
- **Inconvénients:**
  - ⚠️ Nécessite une connexion à l'API
  - ⚠️ Peut ne pas fonctionner pour les petites communes

### Fichiers communs
- **`requirements.txt`** - Dépendances Python nécessaires

---

## 🚀 DÉPLOIEMENT RAPIDE

### Étape 1 : Choisir votre version

**Pour tester rapidement (recommandé en premier):**
```bash
# Renommer le fichier démo en app.py
mv estimateur_demo_streamlit.py app.py
```

**Pour la production (données réelles):**
```bash
# Renommer le fichier DVF en app.py
mv estimateur_immobilier_streamlit.py app.py
```

### Étape 2 : Structure du dépôt

Votre dépôt GitHub doit contenir :
```
votre-repo/
├── app.py (ou streamlit_app.py)
└── requirements.txt
```

### Étape 3 : Déployer sur Streamlit Cloud

1. Allez sur https://share.streamlit.io
2. Connectez votre dépôt GitHub
3. Sélectionnez `app.py` comme fichier principal
4. Cliquez sur **Deploy!**

---

## 🧪 TEST EN LOCAL

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Lancement version démo
```bash
streamlit run estimateur_demo_streamlit.py
```

### Lancement version production
```bash
streamlit run estimateur_immobilier_streamlit.py
```

---

## 🔧 CONFIGURATION

### Codes INSEE utiles

| Ville | Code INSEE |
|-------|-----------|
| Paris | 75056 |
| Marseille | 13055 |
| Lyon | 69123 |
| Toulouse | 31555 |
| Bordeaux | 33063 |
| Lille | 59350 |
| Nantes | 44109 |

🔍 **Trouver un code INSEE:** https://www.insee.fr/fr/recherche/recherche-geographique

### Ajuster les coefficients de standing

Dans les deux fichiers, modifiez ces valeurs :

```python
ajustements = {
    Standing.A_RENOVER: 0.85,      # -15%
    Standing.STANDARD: 1.0,         # Prix de base
    Standing.HAUT_DE_GAMME: 1.20   # +20%
}
```

---

## 🆚 COMPARAISON DES VERSIONS

| Critère | Démo | Production (DVF) |
|---------|------|------------------|
| Source données | Simulées | API officielle |
| Fiabilité | Test uniquement | Production |
| Rapidité | ⚡ Instantané | 🔄 Dépend de l'API |
| Disponibilité | ✅ 100% | ⚠️ Dépend de la commune |
| Usage recommandé | Développement/Test | Utilisation réelle |

---

## ❓ QUELLE VERSION CHOISIR ?

### 🎓 **Débutant / Test**
→ Utilisez `estimateur_demo_streamlit.py`
- Interface fonctionnelle immédiatement
- Pas de problème réseau
- Parfait pour apprendre

### 🏢 **Production / Usage réel**
→ Utilisez `estimateur_immobilier_streamlit.py`
- Données officielles DVF
- Estimations fiables
- Crédibilité professionnelle

### 🔀 **Hybride (recommandé)**
→ Déployez les deux versions :
- `app.py` → Version démo (fallback)
- `app_dvf.py` → Version production
- Ajoutez un bouton de sélection dans Streamlit

---

## 🐛 RÉSOLUTION DE PROBLÈMES

### Erreur "ModuleNotFoundError: matplotlib"
✅ **Solution :** Le fichier contient déjà `matplotlib.use('Agg')` - vérifiez que `requirements.txt` est présent

### Version DVF : "Aucune transaction trouvée"
✅ **Solutions :**
1. Vérifiez le code INSEE sur https://www.insee.fr
2. Essayez une ville plus grande
3. Utilisez la version démo en attendant

### L'application ne démarre pas
✅ **Solutions :**
1. Vérifiez les logs dans "Manage app" → "View logs"
2. Vérifiez que `requirements.txt` est à la racine
3. Redémarrez l'app ("Reboot app")

---

## 📊 EXEMPLE DE RÉSULTATS

### Version Démo
- Transactions simulées : 150
- Prix moyen : ~2 223 €/m²
- Estimation pour 75m² : ~166 746 €

### Version DVF (exemple Bordeaux)
- Transactions réelles : Variable (selon l'année)
- Prix moyen : Données officielles
- Estimation : Basée sur transactions réelles

---

## 🎨 PERSONNALISATION

### Changer le thème

Créez `.streamlit/config.toml` :
```toml
[theme]
primaryColor = "#2ecc71"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Modifier le titre de l'app

Dans le fichier `.py`, ligne ~95 :
```python
st.set_page_config(
    page_title="Votre Titre Ici",
    page_icon="🏠",
)
```

---

## 📞 SUPPORT

**Problèmes courants résolus dans :** `GUIDE_STREAMLIT_DEPLOIEMENT.md`

**Pour plus d'aide :**
- Documentation Streamlit : https://docs.streamlit.io
- API DVF : https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/

---

## ✨ AMÉLIORATIONS FUTURES

- [ ] Ajout d'une carte interactive
- [ ] Export PDF du rapport
- [ ] Comparaison multi-communes
- [ ] Prédictions avec Machine Learning
- [ ] Mode sombre / clair

---

**Bon déploiement ! 🚀**
