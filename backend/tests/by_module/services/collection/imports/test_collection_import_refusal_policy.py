#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-08-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests de la politique de refus global d'import.

import unittest

from services.collection.imports import (
    CollectionImportData,
    CollectionImportGame,
    CollectionImportRefusalPolicy,
    CollectionImportWarnings,
)


class CollectionImportRefusalPolicyTest(unittest.TestCase):
    """Valide le calcul des jeux en erreur utilise pour refuser un fichier."""

    def test_evaluate_counts_invalid_platform_and_missing_mandatory_games(self):
        """Verifie le compteur global des jeux en erreur.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le refus et les compteurs.
        """

        import_data = CollectionImportData(
            platforms=[],
            studios=[],
            games=[CollectionImportGame("Zelda", "Switch", None, None)],
            warnings=CollectionImportWarnings(
                invalid_games=[
                    {"name": "Zelda", "invalid_fields": [{"field": "region"}]},
                ],
                skipped_games=[
                    {"game_name": "Loaded", "imported_platform": "TrouDuc"},
                ],
                skipped_mandatory_games=1,
            ),
        )

        refusal = CollectionImportRefusalPolicy().evaluate(import_data)

        self.assertTrue(refusal.refused)
        self.assertEqual(3, refusal.invalid_games_count)
        self.assertEqual(3, refusal.total_games_count)
        self.assertIn("3/3", refusal.message)


if __name__ == "__main__":
    unittest.main()
