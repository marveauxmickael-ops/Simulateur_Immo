# 🔧 GUIDE DE RÉSOLUTION - Problème de connexion API DVF

## 🚨 Le Problème

L'API `api.cquest.org/dvf` que vous utilisez **n'est plus accessible** ou a été modifiée.

```
❌ Erreur: HTTPSConnectionPool ... Max retries exceeded
```

---

## ✅ LES SOLUTIONS

### Solution 1️⃣ : Utiliser l'API officielle data.gouv.fr (RECOMMANDÉE)

**Avantage** : API officielle et à jour
**Inconvénient** : Format CSV (pas JSON), peut nécessiter plus de parsing

```python
def recuperer_transactions_dvf(code_insee: str):
    departement = code_insee[:2]
    url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/2023/communes/{departement}/{code_insee}.csv"
    
    response = requests.get(url, timeout=15)
    
    if response.status_code == 200:
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        # ... reste du traitement
```

**⚠️ Attention** : Cette API peut aussi être bloquée selon votre environnement réseau.

---

### Solution 2️⃣ : Utiliser l'API DVF+ (Alternative)

```python
url = f"https://app.dvf.etalab.gouv.fr/api/v1/search?code_commune={code_insee}"
```

Cette API renvoie du JSON, plus facile à traiter.

---

### Solution 3️⃣ : Télécharger les fichiers DVF en local

1. Téléchargez les données depuis : https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/
2. Stockez le fichier CSV localement
3. Modifiez votre fonction :

```python
def recuperer_transactions_dvf(code_insee: str):
    # Lecture du fichier local
    df = pd.read_csv('dvf_2023.csv')
    df_commune = df[df['code_commune'] == code_insee]
    # ... filtrage
```

---

### Solution 4️⃣ : Mode Démonstration (pour tester votre code)

J'ai créé `estimateur_demo.py` qui génère des données réalistes pour tester votre application.

**Utilisation** :
```bash
python3 estimateur_demo.py
```

---

## 🔍 DIAGNOSTIC DU PROBLÈME RÉSEAU

Votre environnement semble avoir des **restrictions proxy** :

```
ProxyError: Tunnel connection failed: 403 Forbidden
```

**Causes possibles** :
1. Pare-feu d'entreprise/école
2. Configuration proxy Python
3. Restrictions de sécurité du système

**Solutions** :
- Vérifier les variables d'environnement `HTTP_PROXY` et `HTTPS_PROXY`
- Tester depuis un autre réseau
- Utiliser des données locales (solution 3)

---

## 📊 RÉSULTATS OBTENUS (Mode Démo)

Le script de démonstration fonctionne parfaitement :

```
🏠 VALEUR ESTIMÉE        : 166 746 €
   Fourchette basse (-5%): 158 409 €
   Fourchette haute (+5%): 175 083 €
```

Graphique généré : `evolution_prix_m2.png`

---

## 🎯 PROCHAINES ÉTAPES

1. **Court terme** : Utilisez `estimateur_demo.py` pour développer/tester
2. **Moyen terme** : Téléchargez les fichiers DVF et travaillez en local
3. **Long terme** : Implémentez l'API data.gouv.fr quand le réseau le permettra

---

## 📂 FICHIERS CRÉÉS

- `estimateur_immobilier_fix.py` - Version avec API data.gouv.fr
- `estimateur_demo.py` - Version avec données simulées (FONCTIONNE ✅)
- `evolution_prix_m2.png` - Graphique généré

---

## ❓ BESOIN D'AIDE ?

Si vous avez encore des problèmes :
1. Vérifiez votre connexion internet
2. Testez avec `curl` : `curl https://files.data.gouv.fr`
3. Contactez votre administrateur réseau si en entreprise
