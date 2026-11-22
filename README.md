#  BiblioIIT — Système de Gestion de Bibliothèque

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/Base%20de%20données-SQLite3-003B57?logo=sqlite&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-MVC-ec4899)
![API](https://img.shields.io/badge/API-Open%20Library-10b981)

Application console en **Python** réalisée dans le cadre du cours à l'**Institut Ivoirien de Technologie (IIT)** de Grand-Bassam.  
Elle permet de gérer le catalogue de livres, les emprunts étudiants, les retours et les retards, avec persistance dans **SQLite** (`biblio.sqlite3`) et importation de véritables livres via l'API **Open Library**.

---

##  Fonctionnalités

1. **Rechercher un livre (`1`)** — Recherche par mot-clé (titre, auteur, code ou catégorie) dans `biblio.sqlite3`. Si aucun résultat n'est trouvé localement, l'application propose automatiquement de chercher et d'importer de vrais livres depuis **Open Library**.
2. **Emprunter un livre (`2`)** — Enregistrement par code livre (`L002`) et matricule étudiant (`E2026-001`) :
   - Durée d'emprunt fixée à **14 jours**.
   - Blocage automatique si le livre est **déjà emprunté**.
   - Limite de **3 emprunts actifs** par étudiant.
3. **Rendre un livre (`3`)** — Enregistre la date de retour effective, remet le livre **DISPONIBLE** et signale un éventuel retard.
4. **Afficher les retards (`4`)** — Liste tous les emprunts en cours dont la date de retour prévue est dépassée.
5. **Voir tout le catalogue (`5`)** — Affiche l'ensemble des livres enregistrés dans `biblio.sqlite3` avec leur statut (`DISPONIBLE` / `EMPRUNTÉ`).
6. **Remplir le catalogue (`6`)** — Importe de nouveaux livres réels depuis `openlibrary.org` selon un thème ou un auteur.

---

##  Architecture MVC

```text
Project Gestion_Biblio/
├── main.py                        # Point d'entrée de l'application
├── biblio.sqlite3                 # Base de données SQLite (livres & emprunts)
├── README.md                      # Documentation du projet
├── .gitignore
├── models/                        # Couche Modèle (données, règles & API)
│   ├── __init__.py
│   ├── entites.py                 # Dataclasses Livre et Emprunt
│   ├── regles.py                  # Règles métier (14 jours, max 3 emprunts, retards)
│   ├── depot_sqlite.py            # Requêtes SQLite (CRUD livres & emprunts)
│   └── open_library.py            # Client API Open Library + catalogue réel initial
├── views/                         # Couche Vue (interface terminal)
│   ├── __init__.py
│   └── console_view.py            # Menu, tableaux Unicode et couleurs ANSI
└── controllers/                   # Couche Contrôleur (orchestration)
    ├── __init__.py
    └── biblio_controller.py       # Logique de contrôle entre Modèles et Vue
```

---

## Lancer l'application

Le projet utilise uniquement la **bibliothèque standard Python 3** (aucune dépendance externe à installer) :

```bash
python main.py
```

---

##  Aperçu dans le terminal

```text
╔══════════════════════════════════════════════════════════════╗
║    BiblioIIT — Système de Gestion de Bibliothèque         ║
║   Institut Ivoirien de Technologie    ║
╚══════════════════════════════════════════════════════════════╝

┌───────────────────────── MENU PRINCIPAL ─────────────────────┐
│  1. Rechercher un livre                                      │
│  2. Emprunter un livre                                       │
│  3. Rendre un livre                                          │
│  4. Afficher les retards                                     │
│  5. Voir tout le catalogue                                   │
│  6. Remplir le catalogue (Open Library)                      │
│  0. Quitter                                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Auteure

**Hervé Regina EDERE** — Étudiante en Licence 2 Génie Logiciel, Institut Ivoirien de Technologie (IIT), Grand-Bassam  