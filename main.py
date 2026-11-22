"""Point d'entrée de l'application console BiblioIIT (Architecture MVC)."""

import os
from controllers.biblio_controller import BiblioController
from models.depot_sqlite import DepotSQLite
from views.console_view import ConsoleView


def main() -> None:
    dossier_courant = os.path.dirname(os.path.abspath(__file__))
    chemin_db = os.path.join(dossier_courant, "biblio.sqlite3")

    depot = DepotSQLite(chemin_db)
    vue = ConsoleView()
    controleur = BiblioController(depot, vue)

    try:
        controleur.demarrer()
    finally:
        depot.fermer()


if __name__ == "__main__":
    main()
