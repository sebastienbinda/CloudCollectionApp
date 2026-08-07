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

import services.database.studio_matching_service as studio_matching_service_module
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

    def test_evaluate_existing_studio_reuses_cached_scores(self):
        """Verifie que le matching identique ne recalcule pas les scores.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le cache local du service.
        """

        service = self._service()
        calls = []
        original_score = service._studio_matching_score
        service._studio_matching_score = lambda imported_key, candidate_key: (
            calls.append((imported_key, candidate_key))
            or original_score(imported_key, candidate_key)
        )
        existing_studio_ids = {
            "acclaim studios": 1,
            "nintendo": 2,
        }

        first_result = service.evaluate_existing_studio("Acclaim", existing_studio_ids)
        second_result = service.evaluate_existing_studio("Acclaim", existing_studio_ids)

        self.assertEqual(first_result, second_result)
        self.assertEqual(
            [("acclaim", "acclaim studios"), ("acclaim", "nintendo")],
            calls,
        )

    def test_evaluate_existing_studio_caches_repeated_suffix_alternatives(self):
        """Verifie que les suffixes repetes ne sont pas reevalues par candidat.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le cache des suffixes de studios.
        """

        service = self._service()
        original_matching_score = studio_matching_service_module.matching_score
        suffix_score_calls = []

        def tracked_matching_score(imported_key, candidate_key):
            if imported_key == "sutiods":
                suffix_score_calls.append((imported_key, candidate_key))
            return original_matching_score(imported_key, candidate_key)

        studio_matching_service_module.matching_score = tracked_matching_score
        try:
            service.evaluate_existing_studio(
                "Acclaim",
                {f"team {index} sutiods": index for index in range(1, 101)},
            )
        finally:
            studio_matching_service_module.matching_score = original_matching_score

        self.assertLessEqual(len(suffix_score_calls), len(service.STUDIO_SUFFIX_ALTERNATIVES))

    def _service(self):
        return StudioMatchingService(
            StudioMatchingConfiguration(low_level_rating=25, high_level_rating=87)
        )


if __name__ == "__main__":
    unittest.main()
