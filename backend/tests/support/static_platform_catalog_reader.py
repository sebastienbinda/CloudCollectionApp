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
# Description : lecteur CSV factice pour les tests du seed plateformes.


class StaticPlatformCatalogReader:
    """Lecteur de catalogue factice pour isoler le service de seed."""

    def __init__(self, entries):
        """Initialise le lecteur factice.

        Args:
            entries (list[PlatformCatalogEntry]): Entrees a retourner.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.entries = entries

    def read(self, csv_path):
        """Retourne les entrees configurees.

        Args:
            csv_path (Path): Chemin recu par le service.

        Returns:
            list[PlatformCatalogEntry]: Entrees configurees.
        """

        return self.entries
