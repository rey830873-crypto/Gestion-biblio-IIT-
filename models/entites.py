"""Entités métier de l'application BiblioIIT."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Livre:
    code: str
    titre: str
    auteur: str
    annee: Optional[int] = None
    categorie: str = "Général"


@dataclass
class Emprunt:
    id: Optional[int]
    code_livre: str
    matricule: str
    date_emprunt: date
    date_retour_prevue: date
    date_retour_effective: Optional[date] = None
