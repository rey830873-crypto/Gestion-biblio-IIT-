"""Vue console stylée avec couleurs ANSI et tableaux Unicode pour BiblioIIT."""

import os
from typing import List, Optional, Tuple

from models.entites import Emprunt, Livre


# Active le support des couleurs ANSI dans le terminal Windows
os.system("")

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"


class ConsoleView:
    """Gère tout l'affichage et les saisies utilisateur dans le terminal."""

    @staticmethod
    def afficher_banniere() -> None:
        print(f"\n{MAGENTA}{BOLD}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{MAGENTA}{BOLD}║{RESET}   {CYAN}{BOLD} BiblioIIT — Système de Gestion de Bibliothèque{RESET}         {MAGENTA}{BOLD}║{RESET}")
        print(f"{MAGENTA}{BOLD}║{RESET}   {DIM}Institut Ivoirien de Technologie {RESET}   {MAGENTA}{BOLD}║{RESET}")
        print(f"{MAGENTA}{BOLD}╚══════════════════════════════════════════════════════════════╝{RESET}")

    @staticmethod
    def afficher_menu() -> str:
        print(f"\n{BLUE}{BOLD}┌───────────────────────── MENU PRINCIPAL ─────────────────────┐{RESET}")
        print(f"{BLUE}│{RESET}  {CYAN}1.{RESET} Rechercher un livre                                      {BLUE}│{RESET}")
        print(f"{BLUE}│{RESET}  {CYAN}2.{RESET} Emprunter un livre                                       {BLUE}│{RESET}")
        print(f"{BLUE}│{RESET}  {CYAN}3.{RESET} Rendre un livre                                          {BLUE}│{RESET}")
        print(f"{BLUE}│{RESET}  {CYAN}4.{RESET} Afficher les retards                                     {BLUE}│{RESET}")
        print(f"{BLUE}│{RESET}  {CYAN}5.{RESET} Voir tout le catalogue                                   {BLUE}│{RESET}")
        print(f"{BLUE}│{RESET}  {CYAN}6.{RESET} Remplir le catalogue (Open Library)                      {BLUE}│{RESET}")
        print(f"{BLUE}│{RESET}  {RED}0.{RESET} Quitter                                                  {BLUE}│{RESET}")
        print(f"{BLUE}{BOLD}└──────────────────────────────────────────────────────────────┘{RESET}")
        return input(f"{BOLD}Votre choix : {RESET}").strip()

    @staticmethod
    def demander(invite: str) -> str:
        return input(f"{CYAN}{invite}{RESET}").strip()

    @staticmethod
    def succes(message: str) -> None:
        print(f"\n{GREEN}{BOLD}✔ {message}{RESET}")

    @staticmethod
    def erreur(message: str) -> None:
        print(f"\n{RED}{BOLD}✘ {message}{RESET}")

    @staticmethod
    def info(message: str) -> None:
        print(f"\n{YELLOW}ℹ {message}{RESET}")

    @staticmethod
    def afficher_livres(resultats: List[Tuple[Livre, bool]], titre_section: str = "RÉSULTATS") -> None:
        if not resultats:
            ConsoleView.info("Aucun livre trouvé pour cette recherche.")
            return

        print(f"\n{BOLD}{CYAN}=== {titre_section} ({len(resultats)} livre(s)) ==={RESET}")
        ligne = "─" * 92
        print(f"{DIM}{ligne}{RESET}")
        print(f"{BOLD}{'CODE':<7} │ {'TITRE':<34} │ {'AUTEUR':<22} │ {'ANNÉE':<6} │ {'STATUT'}{RESET}")
        print(f"{DIM}{ligne}{RESET}")

        for livre, disponible in resultats:
            titre_court = (livre.titre[:31] + "...") if len(livre.titre) > 34 else livre.titre
            auteur_court = (livre.auteur[:19] + "...") if len(livre.auteur) > 22 else livre.auteur
            annee_str = str(livre.annee) if livre.annee else "—"
            statut = f"{GREEN}DISPONIBLE{RESET}" if disponible else f"{RED}EMPRUNTÉ{RESET}"
            print(f"{BOLD}{livre.code:<7}{RESET} │ {titre_court:<34} │ {auteur_court:<22} │ {annee_str:<6} │ {statut}")

        print(f"{DIM}{ligne}{RESET}")

    @staticmethod
    def afficher_retards(retards: List[Tuple[Emprunt, Optional[Livre], int]]) -> None:
        if not retards:
            ConsoleView.succes("Aucun emprunt en retard pour le moment !")
            return

        print(f"\n{RED}{BOLD}=== EMPRUNTS EN RETARD ({len(retards)}) ==={RESET}")
        ligne = "─" * 84
        print(f"{DIM}{ligne}{RESET}")
        print(f"{BOLD}{'CODE':<7} │ {'TITRE':<32} │ {'MATRICULE':<12} │ {'PRÉVU LE':<12} │ {'RETARD'}{RESET}")
        print(f"{DIM}{ligne}{RESET}")

        for emprunt, livre, jours in retards:
            titre = livre.titre if livre else "Livre inconnu"
            titre_court = (titre[:29] + "...") if len(titre) > 32 else titre
            print(
                f"{BOLD}{emprunt.code_livre:<7}{RESET} │ {titre_court:<32} │ "
                f"{emprunt.matricule:<12} │ {emprunt.date_retour_prevue.strftime('%d/%m/%Y'):<12} │ "
                f"{RED}{BOLD}{jours} jour(s){RESET}"
            )
        print(f"{DIM}{ligne}{RESET}")
