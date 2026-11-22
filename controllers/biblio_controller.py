"""Contrôleur principal reliant Models (SQLite + Open Library + Règles) et Views (Console)."""

from datetime import date
from typing import List, Optional, Tuple

from models.depot_sqlite import DepotSQLite
from models.entites import Emprunt, Livre
from models.open_library import CATALOGUE_REEL_INITIAL, rechercher_open_library
from models.regles import (
    MAX_EMPRUNTS_PAR_ETUDIANT,
    calculer_date_retour,
    est_en_retard,
    jours_de_retard,
    valider_matricule,
)
from views.console_view import ConsoleView


class BiblioController:
    """Orchestre les opérations de la bibliothèque."""

    def __init__(self, depot: DepotSQLite, view: Optional[ConsoleView] = None):
        self.depot = depot
        self.view = view or ConsoleView()

    def initialiser_catalogue(self) -> int:
        """Remplit la base avec de vrais livres au premier lancement si elle est vide."""
        if self.depot.compter_livres() > 0:
            return 0

        ajoutes = 0
        for item in CATALOGUE_REEL_INITIAL:
            livre = Livre(
                code=item["code"],
                titre=item["titre"],
                auteur=item["auteur"],
                annee=item["annee"],
                categorie=item["categorie"],
            )
            if self.depot.ajouter_livre(livre):
                ajoutes += 1
        return ajoutes

    def rechercher(self, mot_cle: str) -> List[Tuple[Livre, bool]]:
        livres = self.depot.rechercher_livres(mot_cle)
        return [(livre, self.depot.obtenir_emprunt_actif(livre.code) is None) for livre in livres]

    def lister_catalogue(self) -> List[Tuple[Livre, bool]]:
        livres = self.depot.lister_livres()
        return [(livre, self.depot.obtenir_emprunt_actif(livre.code) is None) for livre in livres]

    def emprunter(
        self, code_livre: str, matricule: str, date_emprunt: Optional[date] = None
    ) -> Tuple[bool, str, Optional[Emprunt]]:
        livre = self.depot.obtenir_livre(code_livre)
        if not livre:
            return False, f"Aucun livre trouvé avec le code « {code_livre.strip().upper()} ».", None

        if not valider_matricule(matricule):
            return False, "Matricule invalide (exemple attendu : E2026-001).", None

        emprunt_actif = self.depot.obtenir_emprunt_actif(livre.code)
        if emprunt_actif is not None:
            return False, f"Impossible : Le livre « {livre.titre} » est déjà emprunté.", None

        nb_actifs = self.depot.compter_emprunts_actifs_etudiant(matricule)
        if nb_actifs >= MAX_EMPRUNTS_PAR_ETUDIANT:
            return (
                False,
                f"Impossible : L'étudiant {matricule.upper()} a déjà {MAX_EMPRUNTS_PAR_ETUDIANT} emprunts en cours.",
                None,
            )

        debut = date_emprunt or date.today()
        prevue = calculer_date_retour(debut)
        emprunt = Emprunt(
            id=None,
            code_livre=livre.code,
            matricule=matricule.strip().upper(),
            date_emprunt=debut,
            date_retour_prevue=prevue,
        )
        enregistre = self.depot.enregistrer_emprunt(emprunt)
        return (
            True,
            f"Emprunt enregistré pour « {livre.titre} ». Retour prévu le {prevue.strftime('%d/%m/%Y')}.",
            enregistre,
        )

    def rendre(self, code_livre: str, date_retour: Optional[date] = None) -> Tuple[bool, str]:
        livre = self.depot.obtenir_livre(code_livre)
        if not livre:
            return False, f"Aucun livre trouvé avec le code « {code_livre.strip().upper()} »."

        emprunt = self.depot.obtenir_emprunt_actif(livre.code)
        if not emprunt or emprunt.id is None:
            return False, f"Le livre « {livre.titre} » n'est pas actuellement emprunté."

        retour = date_retour or date.today()
        retard = jours_de_retard(emprunt, retour)
        self.depot.marquer_retour(emprunt.id, retour)

        if retard > 0:
            return True, f"Livre « {livre.titre} » rendu avec {retard} jour(s) de retard."
        return True, f"Livre « {livre.titre} » rendu dans les délais. Merci !"

    def lister_retards(self, date_ref: Optional[date] = None) -> List[Tuple[Emprunt, Optional[Livre], int]]:
        actifs = self.depot.lister_emprunts_actifs()
        retards = []
        for emp in actifs:
            if est_en_retard(emp, date_ref):
                livre = self.depot.obtenir_livre(emp.code_livre)
                retards.append((emp, livre, jours_de_retard(emp, date_ref)))
        return retards

    def importer_open_library(self, sujet: str, limite: int = 5) -> Tuple[bool, str]:
        try:
            trouves = rechercher_open_library(sujet, limite=limite)
        except Exception as exc:
            return False, f"Impossible de joindre Open Library ({exc})."

        if not trouves:
            return False, f"Aucun livre trouvé sur Open Library pour « {sujet} »."

        ajoutes = 0
        for item in trouves:
            code = self.depot.prochain_code_livre()
            livre = Livre(
                code=code,
                titre=item["titre"],
                auteur=item["auteur"],
                annee=item["annee"],
                categorie=item["categorie"],
            )
            if self.depot.ajouter_livre(livre):
                ajoutes += 1

        return True, f"{ajoutes} nouveau(x) livre(s) réel(s) importé(s) depuis Open Library !"

    # -------------------- BOUCLE CONSOLE --------------------

    def demarrer(self) -> None:
        self.view.afficher_banniere()
        nb = self.initialiser_catalogue()
        if nb > 0:
            self.view.info(f"Base SQLite initialisée avec {nb} livres réels.")

        while True:
            choix = self.view.afficher_menu()

            if choix == "1":
                mot_cle = self.view.demander("Mot-clé (titre, auteur ou code) : ")
                resultats = self.rechercher(mot_cle)
                if resultats:
                    self.view.afficher_livres(resultats, f"RECHERCHE : {mot_cle}")
                else:
                    self.view.info(f"Aucun livre trouvé en local pour « {mot_cle} ».")
                    rep = self.view.demander("Chercher et importer depuis Open Library ? (o/n) : ").lower()
                    if rep in ("o", "oui", "y", "yes"):
                        ok, msg = self.importer_open_library(mot_cle, limite=5)
                        (self.view.succes if ok else self.view.erreur)(msg)
                        if ok:
                            self.view.afficher_livres(self.rechercher(mot_cle), f"IMPORTÉS : {mot_cle}")

            elif choix == "2":
                code = self.view.demander("Code du livre (ex: L002) : ")
                matricule = self.view.demander("Matricule étudiant (ex: E2026-001) : ")
                ok, msg, _ = self.emprunter(code, matricule)
                (self.view.succes if ok else self.view.erreur)(msg)

            elif choix == "3":
                code = self.view.demander("Code du livre à rendre : ")
                ok, msg = self.rendre(code)
                (self.view.succes if ok else self.view.erreur)(msg)

            elif choix == "4":
                self.view.afficher_retards(self.lister_retards())

            elif choix == "5":
                self.view.afficher_livres(self.lister_catalogue(), "CATALOGUE COMPLET")

            elif choix == "6":
                sujet = self.view.demander("Sujet ou auteur à importer depuis Open Library (ex: python, kourouma) : ")
                ok, msg = self.importer_open_library(sujet, limite=5)
                (self.view.succes if ok else self.view.erreur)(msg)

            elif choix == "0":
                self.view.info("À bientôt sur BiblioIIT !")
                break

            else:
                self.view.erreur("Choix invalide. Veuillez entrer un chiffre entre 0 et 6.")
