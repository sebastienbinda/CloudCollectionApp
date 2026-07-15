#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-15
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du matching des studios importes.

import unittest

from services.database import StudioMatchingConfiguration, StudioMatchingService


class StudioMatchingServiceTest(unittest.TestCase):
    """Valide le rattachement des studios au referentiel."""

    def test_match_existing_studio_key_accepts_exact_case_accent_and_typo(self):
        """Verifie les correspondances fiables.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les rattachements.
        """

        service = self._service()
        existing_studio_ids = {
            "nintendo": 1,
            "acclaim studios": 2,
            "ubisoft montreal": 3,
        }

        self.assertEqual(
            "nintendo",
            service.match_existing_studio_key("Nintendô", existing_studio_ids),
        )
        self.assertEqual(
            "acclaim studios",
            service.match_existing_studio_key("Acclaim", existing_studio_ids),
        )
        self.assertEqual(
            "ubisoft montreal",
            service.match_existing_studio_key("Ubisoft Montréal", existing_studio_ids),
        )

    def test_match_existing_studio_key_accepts_acclaim_requested_variants(self):
        """Verifie les equivalences Acclaim demandees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les rattachements.
        """

        service = self._service()

        self.assertEqual(
            "accclaim entertainment",
            service.match_existing_studio_key("Acclaim", {"accclaim entertainment": 7}),
        )
        self.assertEqual(
            "acclaim sutiods",
            service.match_existing_studio_key("Acclaim", {"acclaim sutiods": 8}),
        )
        self.assertEqual(
            "acclaim games",
            service.match_existing_studio_key("Acclaim", {"acclaim games": 9}),
        )

    def test_match_existing_studio_key_rejects_low_score_and_ambiguity(self):
        """Verifie les refus faute de correspondance unique.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les refus.
        """

        service = self._service()

        self.assertIsNone(service.match_existing_studio_key("Rare", {"square enix": 1}))
        self.assertIsNone(
            service.match_existing_studio_key("Ubisoft", {"ubisoft montreal": 2})
        )
        self.assertIsNone(
            service.match_existing_studio_key("Ubisoft Mainz", {"ubisoft milan": 3})
        )
        self.assertIsNone(
            service.match_existing_studio_key(
                "Acclaim",
                {
                    "acclaim studios": 1,
                    "acclaim sutiods": 2,
                },
            )
        )

    def _service(self):
        return StudioMatchingService(
            StudioMatchingConfiguration(low_level_rating=25, high_level_rating=87)
        )


if __name__ == "__main__":
    unittest.main()
