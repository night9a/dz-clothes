# DZ Clothes

Site e‑commerce moderne (Flask + React) en français et arabe : inscription, vérification email, panier, paiement Baridi Mob, panneau admin avec statistiques, produits, réductions et notifications Telegram.

## Stack

- **Backend:** Flask, PostgreSQL (Aiven), JWT, Resend (email), Telegram API
- **Frontend:** React (Vite), i18next (FR/AR), Recharts

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Éditer .env : DATABASE_URL, JWT_SECRET_KEY, RESEND_API_KEY (ou SMTP), TELEGRAM_BOT_TOKEN
python -c "from app import app; from db import init_db; init_db()"  # ou lancer une fois l'app
flask run
# ou: python app.py  (écoute sur http://0.0.0.0:5000)
```

- **Base de données:** utiliser l’URL PostgreSQL fournie (Aiven) dans `DATABASE_URL`.
- **Email:** SMTP dans `.env` (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`). Ex. Gmail : `smtp.gmail.com`, port `587`, votre adresse Gmail et un mot de passe d’application. Sans SMTP, le lien de vérification est affiché dans la console du backend.
- **Telegram:** créer un bot avec [@BotFather](https://t.me/BotFather), mettre le token dans `TELEGRAM_BOT_TOKEN`. Pour recevoir les notifications, envoyer `/start` au bot puis copier le Chat ID dans Admin > Paramètres > Telegram (ou dans `TELEGRAM_ADMIN_CHAT_ID`).

### Bot Telegram (optionnel)

Pour enregistrer le Chat ID via le bot :

```bash
cd backend
python telegram_bot.py
```

Envoyez `/start` à votre bot ; il vous renverra votre Chat ID. Utilisez-le dans l’admin ou dans `.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Ouvrir http://localhost:5173. Le proxy Vite envoie `/api` vers le backend (port 5000).

### Accès admin

Connectez-vous avec **admin@admin.com** / **123** (créé au premier lancement du backend). Le lien « Administration » dans la barre de navigation mène au tableau de bord (/admin). Le premier utilisateur inscrit et vérifié par email peut aussi être admin.

## Fonctionnalités

- **Client:** inscription, vérification email, connexion, boutique (FR/AR), panier (session ou compte), checkout avec formulaire Baridi Mob (téléphone + référence), code promo.
- **Admin:** tableau de bord (commandes, ventes, graphique), liste et statut des commandes, CRUD produits, CRUD réductions, paramètres Telegram pour recevoir une notification à chaque nouvelle commande.

## Footer

En bas de page : « Créé par mosho » avec lien Instagram https://www.instagram.com/mosho_tenx/

## Licence

Projet personnel / éducatif.
