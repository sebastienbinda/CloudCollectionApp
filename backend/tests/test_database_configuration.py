#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#

import os
import unittest
from unittest.mock import patch

from services.database import DatabaseConfiguration, DatabaseModelBase


class DatabaseConfigurationTest(unittest.TestCase):
    def test_database_models_expose_initial_schema_tables(self):
        """Verifie que les modeles ORM couvrent le schema initial.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les tables ORM declarees.
        """

        self.assertEqual(
            {
                "t_schema_version",
                "t_platform",
                "t_studio",
                "t_user",
                "t_game",
                "t_user_collection",
            },
            set(DatabaseModelBase.metadata.tables.keys()),
        )

    def test_from_environment_reads_database_settings(self):
        """Verifie la lecture des variables d'environnement SQL.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la configuration construite.
        """

        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:password@database:5432/app",
                "DB_SCHEMA_NAME": "collection_schema",
                "APP_VERSION": "1.2",
            },
            clear=True,
        ):
            configuration = DatabaseConfiguration.from_environment()

        self.assertEqual(
            "postgresql+psycopg://user:password@database:5432/app",
            configuration.database_url,
        )
        self.assertEqual("collection_schema", configuration.schema_name)
        self.assertEqual("1.2", configuration.application_version)

    def test_validate_rejects_unsafe_schema_name(self):
        """Verifie le refus des noms de schema non surs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        configuration = DatabaseConfiguration(
            database_url="postgresql://database/app",
            schema_name="public;drop",
            application_version="1.0",
        )

        with self.assertRaises(ValueError):
            configuration.validate()

    def test_validate_rejects_long_application_version(self):
        """Verifie la contrainte de taille de `t_schema_version.version`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur attendue.
        """

        configuration = DatabaseConfiguration(
            database_url="postgresql://database/app",
            schema_name="collection",
            application_version="2026.05",
        )

        with self.assertRaises(ValueError):
            configuration.validate()


if __name__ == "__main__":
    unittest.main()
