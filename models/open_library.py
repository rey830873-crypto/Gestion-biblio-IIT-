"""Client API Open Library pour récupérer de véritables livres réels."""

import json
import urllib.parse
import urllib.request
from typing import List, Dict, Any


OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"

# Catalogue réel de secours (utilisé si hors-ligne ou au démarrage initial)
CATALOGUE_REEL_INITIAL: List[Dict[str, Any]] = [
    {"code": "L001", "titre": "Climbié", "auteur": "Bernard Dadié", "annee": 1956, "categorie": "Littérature"},
    {"code": "L002", "titre": "Les Soleils des indépendances", "auteur": "Ahmadou Kourouma", "annee": 1968, "categorie": "Littérature"},
    {"code": "L003", "titre": "Une si longue lettre", "auteur": "Mariama Bâ", "annee": 1979, "categorie": "Littérature"},
    {"code": "L004", "titre": "Allah n'est pas obligé", "auteur": "Ahmadou Kourouma", "annee": 2000, "categorie": "Littérature"},
    {"code": "L005", "titre": "L'Enfant noir", "auteur": "Camara Laye", "annee": 1953, "categorie": "Littérature"},
    {"code": "L006", "titre": "Clean Code", "auteur": "Robert C. Martin", "annee": 2008, "categorie": "Génie Logiciel"},
    {"code": "L007", "titre": "Python Crash Course", "auteur": "Eric Matthes", "annee": 2015, "categorie": "Python"},
    {"code": "L008", "titre": "Database System Concepts", "auteur": "Abraham Silberschatz", "annee": 1986, "categorie": "Bases de données"},
]


def rechercher_open_library(requete: str, limite: int = 5, timeout: int = 6) -> List[Dict[str, Any]]:
    """Interroge l'API Open Library et retourne une liste de vrais livres."""
    params = urllib.parse.urlencode({"q": requete, "limit": limite})
    url = f"{OPEN_LIBRARY_SEARCH_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "BiblioIIT/1.0 (Projet Etudiant)"})

    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    resultats: List[Dict[str, Any]] = []
    for doc in payload.get("docs", []):
        titre = doc.get("title")
        if not titre:
            continue
        auteurs = doc.get("author_name") or ["Auteur inconnu"]
        annee = doc.get("first_publish_year")
        subjects = doc.get("subject") or []
        categorie = subjects[0] if subjects else "Open Library"
        resultats.append({
            "titre": str(titre).strip(),
            "auteur": ", ".join(auteurs[:2]),
            "annee": int(annee) if isinstance(annee, int) else None,
            "categorie": str(categorie)[:30],
        })
    return resultats
