"""Couche d'accès aux données SQLite pour BiblioIIT."""

import sqlite3
from datetime import date
from typing import List, Optional

from models.entites import Emprunt, Livre


class DepotSQLite:
    """Gère la persistance des livres et emprunts dans SQLite."""

    def __init__(self, chemin_db: str = "biblio.sqlite3"):
        self.chemin_db = chemin_db
        self.conn = sqlite3.connect(self.chemin_db)
        self.conn.row_factory = sqlite3.Row
        self._initialiser_tables()

    def _initialiser_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS livres (
                code TEXT PRIMARY KEY,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                annee INTEGER,
                categorie TEXT NOT NULL DEFAULT 'Général'
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS emprunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_livre TEXT NOT NULL,
                matricule TEXT NOT NULL,
                date_emprunt TEXT NOT NULL,
                date_retour_prevue TEXT NOT NULL,
                date_retour_effective TEXT,
                FOREIGN KEY (code_livre) REFERENCES livres(code)
            )
            """
        )
        self.conn.commit()

    def fermer(self) -> None:
        self.conn.close()

    # -------------------- LIVRES --------------------

    def ajouter_livre(self, livre: Livre) -> bool:
        """Ajoute un livre s'il n'existe pas déjà (par code ou titre exact)."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM livres WHERE code = ? OR LOWER(titre) = LOWER(?)", (livre.code, livre.titre))
        if cur.fetchone():
            return False
        cur.execute(
            "INSERT INTO livres (code, titre, auteur, annee, categorie) VALUES (?, ?, ?, ?, ?)",
            (livre.code.upper(), livre.titre, livre.auteur, livre.annee, livre.categorie),
        )
        self.conn.commit()
        return True

    def compter_livres(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM livres")
        return int(cur.fetchone()[0])

    def prochain_code_livre(self) -> str:
        """Génère le prochain code livre (ex: L009)."""
        cur = self.conn.cursor()
        cur.execute("SELECT code FROM livres WHERE code LIKE 'L%' ORDER BY code DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            return "L001"
        try:
            num = int(row["code"][1:]) + 1
        except ValueError:
            num = self.compter_livres() + 1
        return f"L{num:03d}"

    def obtenir_livre(self, code: str) -> Optional[Livre]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM livres WHERE UPPER(code) = UPPER(?)", (code.strip(),))
        row = cur.fetchone()
        return self._row_vers_livre(row) if row else None

    def lister_livres(self) -> List[Livre]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM livres ORDER BY code ASC")
        return [self._row_vers_livre(r) for r in cur.fetchall()]

    def rechercher_livres(self, mot_cle: str) -> List[Livre]:
        motif = f"%{mot_cle.strip()}%"
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM livres
            WHERE LOWER(titre) LIKE LOWER(?)
               OR LOWER(auteur) LIKE LOWER(?)
               OR LOWER(code) LIKE LOWER(?)
               OR LOWER(categorie) LIKE LOWER(?)
            ORDER BY code ASC
            """,
            (motif, motif, motif, motif),
        )
        return [self._row_vers_livre(r) for r in cur.fetchall()]

    # -------------------- EMPRUNTS --------------------

    def enregistrer_emprunt(self, emprunt: Emprunt) -> Emprunt:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO emprunts (code_livre, matricule, date_emprunt, date_retour_prevue, date_retour_effective)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                emprunt.code_livre.upper(),
                emprunt.matricule.strip().upper(),
                emprunt.date_emprunt.isoformat(),
                emprunt.date_retour_prevue.isoformat(),
                emprunt.date_retour_effective.isoformat() if emprunt.date_retour_effective else None,
            ),
        )
        self.conn.commit()
        emprunt.id = cur.lastrowid
        return emprunt

    def obtenir_emprunt_actif(self, code_livre: str) -> Optional[Emprunt]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM emprunts
            WHERE UPPER(code_livre) = UPPER(?) AND date_retour_effective IS NULL
            ORDER BY id DESC LIMIT 1
            """,
            (code_livre.strip(),),
        )
        row = cur.fetchone()
        return self._row_vers_emprunt(row) if row else None

    def compter_emprunts_actifs_etudiant(self, matricule: str) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) FROM emprunts
            WHERE UPPER(matricule) = UPPER(?) AND date_retour_effective IS NULL
            """,
            (matricule.strip(),),
        )
        return int(cur.fetchone()[0])

    def lister_emprunts_actifs(self) -> List[Emprunt]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM emprunts WHERE date_retour_effective IS NULL ORDER BY date_retour_prevue ASC"
        )
        return [self._row_vers_emprunt(r) for r in cur.fetchall()]

    def marquer_retour(self, emprunt_id: int, date_retour: date) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE emprunts SET date_retour_effective = ? WHERE id = ?",
            (date_retour.isoformat(), emprunt_id),
        )
        self.conn.commit()

    # -------------------- HELPERS --------------------

    @staticmethod
    def _row_vers_livre(row: sqlite3.Row) -> Livre:
        return Livre(
            code=row["code"],
            titre=row["titre"],
            auteur=row["auteur"],
            annee=row["annee"],
            categorie=row["categorie"],
        )

    @staticmethod
    def _row_vers_emprunt(row: sqlite3.Row) -> Emprunt:
        return Emprunt(
            id=row["id"],
            code_livre=row["code_livre"],
            matricule=row["matricule"],
            date_emprunt=date.fromisoformat(row["date_emprunt"]),
            date_retour_prevue=date.fromisoformat(row["date_retour_prevue"]),
            date_retour_effective=(
                date.fromisoformat(row["date_retour_effective"])
                if row["date_retour_effective"]
                else None
            ),
        )
