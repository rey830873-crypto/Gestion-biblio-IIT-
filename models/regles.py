"""Règles métier pour la gestion des emprunts BiblioIIT."""

from datetime import date, timedelta
from typing import Optional

from models.entites import Emprunt

DUREE_EMPRUNT_JOURS = 14
MAX_EMPRUNTS_PAR_ETUDIANT = 3


def calculer_date_retour(date_debut: date, duree_jours: int = DUREE_EMPRUNT_JOURS) -> date:
    """Calcule la date de retour prévue à partir de la date d'emprunt."""
    return date_debut + timedelta(days=duree_jours)


def est_en_retard(emprunt: Emprunt, date_ref: Optional[date] = None) -> bool:
    """Retourne True si l'emprunt actif a dépassé sa date de retour prévue."""
    if emprunt.date_retour_effective is not None:
        return False
    ref = date_ref or date.today()
    return ref > emprunt.date_retour_prevue


def jours_de_retard(emprunt: Emprunt, date_ref: Optional[date] = None) -> int:
    """Retourne le nombre de jours de retard (0 si à l'heure)."""
    if not est_en_retard(emprunt, date_ref):
        return 0
    ref = date_ref or date.today()
    return (ref - emprunt.date_retour_prevue).days


def valider_matricule(matricule: str) -> bool:
    """Vérifie qu'un matricule étudiant est non vide et contient au moins 4 caractères."""
    return bool(matricule and len(matricule.strip()) >= 4)
