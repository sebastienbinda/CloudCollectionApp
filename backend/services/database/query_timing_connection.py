#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _\| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-21
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : proxy SQLAlchemy de mesure des durees de requetes.

from time import perf_counter

from sqlalchemy.engine import Connection


class QueryTimingConnection:
    """Mesure le temps cumule des executions SQL d'une connexion."""

    def __init__(self, connection: Connection):
        """Initialise le proxy de connexion chronometre.

        Args:
            connection (Connection): Connexion SQLAlchemy transactionnelle.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection
        self.query_duration_seconds = 0.0

    def execute(self, *args, **kwargs):
        """Execute une requete SQL en cumulant sa duree.

        Args:
            *args: Arguments transmis a SQLAlchemy.
            **kwargs: Arguments nommes transmis a SQLAlchemy.

        Returns:
            object: Resultat SQLAlchemy de l'execution.
        """

        started_at = perf_counter()
        try:
            return self.connection.execute(*args, **kwargs)
        finally:
            self.query_duration_seconds += max(0.0, perf_counter() - started_at)

    def __getattr__(self, name: str):
        """Delegue les attributs non chronometres a la connexion source.

        Args:
            name (str): Nom d'attribut demande.

        Returns:
            object: Attribut expose par la connexion SQLAlchemy.
        """

        return getattr(self.connection, name)
