#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-07
# Auteurs : Codex et Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du resolver objet de chemin ODS.
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.ods import OdsPathResolver


class OdsPathResolverTest(unittest.TestCase):
    """Valide la resolution du fichier collection.ods du projet."""

    def test_resolve_returns_explicit_path_first(self):
        """Verifie que le chemin explicite est prioritaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin resolu.
        """

        self.assertEqual("/tmp/custom.ods", OdsPathResolver("/tmp/custom.ods").resolve())

    def test_resolve_returns_environment_path_before_default(self):
        """Verifie que la variable d'environnement reste prioritaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin resolu.
        """

        with tempfile.TemporaryDirectory() as directory:
            ods_path = f"{directory}/env.ods"
            Path(ods_path).touch()
            previous_path = os.environ.get("JEUXVIDEO_ODS_PATH")
            os.environ["JEUXVIDEO_ODS_PATH"] = ods_path
            try:
                self.assertEqual(ods_path, OdsPathResolver().resolve())
            finally:
                if previous_path is None:
                    os.environ.pop("JEUXVIDEO_ODS_PATH", None)
                else:
                    os.environ["JEUXVIDEO_ODS_PATH"] = previous_path

    def test_resolve_returns_project_collection_by_default(self):
        """Verifie que collection.ods du projet est le chemin par defaut.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le chemin resolu.
        """

        previous_path = os.environ.pop("JEUXVIDEO_ODS_PATH", None)
        try:
            expected_path = str(Path(__file__).resolve().parents[2] / "collection.ods")
            self.assertEqual(expected_path, OdsPathResolver().resolve())
        finally:
            if previous_path is not None:
                os.environ["JEUXVIDEO_ODS_PATH"] = previous_path


if __name__ == "__main__":
    unittest.main()
