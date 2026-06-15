#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : connexion SQL factice pour les tests du catalogue plateformes.

from tests.fake_platform_catalog_result import FakePlatformCatalogResult


class FakePlatformCatalogConnection:
    """Connexion factice capturant les insertions de plateformes."""

    def __init__(self, existing_rows=None):
        """Initialise la connexion factice.

        Args:
            existing_rows (list[dict] | None): Plateformes deja presentes.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.existing_rows = existing_rows or []
        self.executed_statements = []

    def execute(self, statement, parameters=None):
        """Capture une requete SQL.

        Args:
            statement (object): Requete SQLAlchemy.
            parameters (dict | None): Parametres SQL.

        Returns:
            FakePlatformCatalogResult: Resultat factice.
        """

        self.executed_statements.append((str(statement), parameters or {}))
        if str(statement).startswith("SELECT name"):
            return FakePlatformCatalogResult(self.existing_rows)
        if str(statement).startswith("SELECT id, name"):
            return FakePlatformCatalogResult(self.existing_rows)
        if str(statement).startswith("SELECT platform, name"):
            return FakePlatformCatalogResult(self.existing_rows)
        return FakePlatformCatalogResult()
