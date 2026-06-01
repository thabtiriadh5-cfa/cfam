# CFAM — Gestion des Stagiaires
## Centre de Formation et d'Apprentissage MSAKEN

Application web de gestion des stagiaires hébergée sur Render.com

---

## 🚀 Déploiement sur Render.com (GRATUIT)

### Étape 1 — Créer un compte GitHub
1. Va sur https://github.com et crée un compte gratuit
2. Crée un **nouveau dépôt** (New repository) nommé `cfam`
3. Coche "Public" et clique "Create repository"

### Étape 2 — Uploader les fichiers
Dans ton dépôt GitHub, clique "uploading an existing file" et uploade **tous les fichiers** du dossier `cfam/` :
- `app.py`
- `requirements.txt`
- `render.yaml`
- `seed_data.json`
- `templates/login.html`
- `templates/dashboard.html`

### Étape 3 — Créer le service sur Render
1. Va sur https://render.com et connecte-toi avec GitHub
2. Clique **"New +"** → **"Web Service"**
3. Sélectionne ton dépôt `cfam`
4. Render détecte automatiquement `render.yaml`
5. Clique **"Create Web Service"**

### Étape 4 — Créer la base de données
1. Sur Render, clique **"New +"** → **"PostgreSQL"**
2. Nom : `cfam-db`
3. Plan : **Free**
4. Clique "Create Database"
5. Copie l'**Internal Database URL**
6. Dans ton Web Service → Environment → ajoute :
   - `DATABASE_URL` = (colle l'URL copiée)

### Étape 5 — Accès
Ton app sera disponible sur : `https://cfam.onrender.com`

---

## 🔐 Identifiants de connexion
- **Login :** `51541`
- **Mot de passe :** `r51541`

---

## 📋 Fonctionnalités
- ✅ Gestion complète des stagiaires (ajout, modification, suppression)
- ✅ 4 promotions pré-chargées (444 stagiaires)
- ✅ Recherche et filtres par groupe / spécialité
- ✅ Attestations imprimables (inscription, présence, réussite)
- ✅ Liste nominative par groupe
- ✅ Gestion dynamique des promotions
- ✅ Interface bilingue (FR / AR)
- ✅ Accessible depuis n'importe quel appareil

---

## ⚠️ Note sur le plan gratuit Render
- L'app se "met en veille" après 15 min d'inactivité
- Premier chargement peut prendre 30-60 secondes
- Base de données gratuite : 1 Go max, 90 jours puis expire
- Pour éviter l'expiration : passer au plan "Starter" (7$/mois)
