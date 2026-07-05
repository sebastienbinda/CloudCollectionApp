#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du matching centralise des jeux importes.

import unittest

from services.collection.imports import CollectionImportGame
from services.database import GameMatchingConfiguration, GameMatchingService
from services.users import UserCollectionNameNormalizer


class GameMatchingServiceTest(unittest.TestCase):
    """Valide le rattachement des jeux importes aux jeux existants."""

    def setUp(self):
        """Prepare un service de matching avec seuil haut controle.

        Args:
            Aucun.

        Returns:
            None: La methode initialise le test.
        """

        self.service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=75),
            UserCollectionNameNormalizer(),
        )

    def test_find_existing_game_id_returns_exact_match_first(self):
        """Verifie que le rattachement exact reste prioritaire.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'identifiant retenu.
        """

        game = CollectionImportGame("Zelda", "Switch", None, None)

        game_id = self.service.find_existing_game_id(
            game,
            {
                ("switch", "zelda"): 7,
                ("switch", "the legend of zelda"): 9,
            },
            {
                "switch": [("zelda", 7), ("the legend of zelda", 9)],
            },
        )

        self.assertEqual(7, game_id)

    def test_find_existing_game_id_uses_stored_game_key_before_fuzzy_score(self):
        """Verifie le rattachement exact apres standardisation du nom de jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'identifiant retenu sans score fuzzy.
        """

        strict_service = GameMatchingService(
            GameMatchingConfiguration(low_level_rating=25, high_level_rating=99),
            UserCollectionNameNormalizer(),
        )
        game = CollectionImportGame("Burnout 3\xa0: Takedown", "PlayStation 2", None, None)

        result = strict_service.evaluate_existing_game(
            game,
            {("playstation 2", "burnout 3 : takedown"): 107},
            {"playstation 2": [("burnout 3 : takedown", 107)]},
        )

        self.assertEqual(107, result.existing_game_id)
        self.assertIsNone(result.best_candidate)

    def test_find_existing_game_id_accepts_unique_high_score_on_same_platform(self):
        """Verifie le rattachement par score eleve et unique sur la meme plateforme.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'identifiant retenu.
        """

        game = CollectionImportGame("Legend of Zelda", "Switch", None, None)

        existing_game_ids = {
            ("switch", "the legend of zelda"): 11,
            ("nes", "legend of zelda"): 13,
            ("switch", "mario kart"): 17,
        }
        game_id = self.service.find_existing_game_id(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_ids),
        )

        self.assertEqual(11, game_id)

    def test_find_existing_game_id_rejects_low_score_and_ambiguous_score(self):
        """Verifie qu'un score insuffisant ou ambigu ne rattache pas le jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de rattachement.
        """

        low_score_game = CollectionImportGame("Zelda", "Switch", None, None)
        ambiguous_game = CollectionImportGame("Test", "Switch", None, None)

        low_score_id = self.service.find_existing_game_id(
            low_score_game,
            {("switch", "mario kart"): 17},
            {"switch": [("mario kart", 17)]},
        )
        ambiguous_id = self.service.find_existing_game_id(
            ambiguous_game,
            {
                ("switch", "test a"): 19,
                ("switch", "test b"): 23,
            },
            {"switch": [("test a", 19), ("test b", 23)]},
        )

        self.assertIsNone(low_score_id)
        self.assertIsNone(ambiguous_id)

    def test_find_existing_game_id_rejects_base_title_against_numbered_sequel(self):
        """Verifie qu'un jeu de base ne matche pas sa suite numerotee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de rattachement.
        """

        game = CollectionImportGame("Final Fantasy", "NES", None, None)
        existing_game_ids = {("nes", "final fantasy 2"): 17}

        result = self.service.evaluate_existing_game(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_ids),
        )

        self.assertIsNone(result.existing_game_id)
        self.assertEqual(0, result.best_candidate.score)

    def test_find_existing_game_id_accepts_equivalent_arabic_and_roman_suffixes(self):
        """Verifie le matching eleve entre chiffres arabes et romains.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le rattachement de la suite equivalente.
        """

        game = CollectionImportGame("Final Fantasy 3", "NES", None, None)
        existing_game_ids = {("nes", "final fantasy iii"): 23}

        result = self.service.evaluate_existing_game(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_ids),
        )

        self.assertEqual(23, result.existing_game_id)
        self.assertEqual(100, result.best_candidate.score)

    def test_find_existing_game_id_rejects_different_numbered_sequels(self):
        """Verifie que deux suites numerotees differentes ne matchent pas.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'absence de rattachement.
        """

        game = CollectionImportGame("Final Fantasy 3", "NES", None, None)
        existing_game_ids = {("nes", "final fantasy 2"): 17}

        result = self.service.evaluate_existing_game(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_ids),
        )

        self.assertIsNone(result.existing_game_id)
        self.assertEqual(0, result.best_candidate.score)

    def test_find_existing_game_id_rejects_main_episode_against_hyphenated_sequel(self):
        """Verifie qu'un episode principal ne matche pas sa suite avec tiret.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score force a zero.
        """

        game = CollectionImportGame("Final Fantasy X", "PS2", None, None)
        existing_game_ids = {("ps2", "final fantasy x-2"): 17}

        result = self.service.evaluate_existing_game(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_ids),
        )

        self.assertIsNone(result.existing_game_id)
        self.assertEqual(0, result.best_candidate.score)

    def test_calculate_name_score_reuses_game_sequel_rules(self):
        """Verifie le calcul direct du score metier entre deux noms.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les regles de suite.
        """

        score = self.service.calculate_name_score("Final X", "Final X-2")

        self.assertEqual(0, score)

    def test_calculate_name_score_rejects_numeric_suffix_with_extra_content(self):
        """Verifie le refus d'un suffixe numerique suivi d'un complement.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score force a zero.
        """

        score = self.service.calculate_name_score("Final Fantasy X", "Final Fantasy X-2.2")

        self.assertEqual(0, score)

    def test_calculate_name_score_rejects_different_series_number_with_extra_text(self):
        """Verifie le refus d'un numero de serie different suivi de texte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score force a zero.
        """

        score = self.service.calculate_name_score(
            "Final Fantasy 10",
            "Final Fantasy 11 yOs",
        )

        self.assertEqual(0, score)

    def test_calculate_name_score_rejects_different_series_number_with_typo(self):
        """Verifie le refus d'un numero de serie different malgre une faute.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score force a zero.
        """

        score = self.service.calculate_name_score(
            "Final Fantasy 10",
            "Final Fantsy 11 le ",
        )

        self.assertEqual(0, score)

    def test_calculate_name_score_accepts_equivalent_series_number_with_typo(self):
        """Verifie l'acceptation d'un numero de serie equivalent malgre une faute.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score force a cent.
        """

        roman_score = self.service.calculate_name_score(
            "Final Fantasy 10",
            "Final Fantsy X",
        )
        arabic_score = self.service.calculate_name_score(
            "Final Fantasy 10",
            "Final Fantsy 10",
        )

        self.assertEqual(100, roman_score)
        self.assertEqual(100, arabic_score)

    def test_explain_name_score_identifies_numeric_suffix_extension(self):
        """Verifie le diagnostic d'un suffixe numerique prolonge.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la regle de rejet.
        """

        result = self.service.explain_name_score(
            "Final Fantasy X",
            "Final Fantasy X-2.2",
        )

        self.assertEqual(0, result.score)
        self.assertEqual("rejected", result.decision.value)
        self.assertEqual("numeric_suffix_extension", result.rule)

    def test_explain_name_score_identifies_different_series_number_with_extra_text(self):
        """Verifie le diagnostic d'un numero de serie different suivi de texte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la regle de rejet.
        """

        result = self.service.explain_name_score(
            "Final Fantasy 10",
            "Final Fantasy 11 yOs",
        )

        self.assertEqual(0, result.score)
        self.assertEqual("rejected", result.decision.value)
        self.assertEqual("different_numeric_suffix", result.rule)

    def test_explain_name_score_identifies_different_series_number_with_typo(self):
        """Verifie le diagnostic d'un numero de serie different avec faute.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la regle de rejet.
        """

        result = self.service.explain_name_score(
            "Final Fantasy 10",
            "Final Fantsy 11 le ",
        )

        self.assertEqual(0, result.score)
        self.assertEqual("rejected", result.decision.value)
        self.assertEqual("different_numeric_suffix", result.rule)

    def test_explain_name_score_identifies_equivalent_series_number_with_typo(self):
        """Verifie le diagnostic d'un numero equivalent avec faute.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la regle d'acceptation.
        """

        result = self.service.explain_name_score(
            "Final Fantasy 10",
            "Final Fantsy X",
        )

        self.assertEqual(100, result.score)
        self.assertEqual("accepted", result.decision.value)
        self.assertEqual("equivalent_numeric_suffix", result.rule)

    def test_calculate_name_score_rejects_different_word_suffix_in_same_series(self):
        """Verifie le refus de deux jeux de meme serie avec suffixe different.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score force a zero.
        """

        score = self.service.calculate_name_score("Monster Hunter Wild", "Monster Hunter World")

        self.assertEqual(0, score)

    def test_explain_name_score_identifies_different_final_word(self):
        """Verifie le diagnostic de deux titres proches avec dernier mot different.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la regle de rejet.
        """

        result = self.service.explain_name_score(
            "Monster Hunter Wild",
            "Monster Hunter World",
        )

        self.assertEqual(0, result.score)
        self.assertEqual("rejected", result.decision.value)
        self.assertEqual("different_final_word", result.rule)

    def test_calculate_name_score_keeps_optional_prefix_matching_available(self):
        """Verifie qu'un prefixe optionnel ne declenche pas le rejet par suffixe.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident un score fuzzy encore eleve.
        """

        score = self.service.calculate_name_score("Legend of Zelda", "The Legend of Zelda")

        self.assertGreaterEqual(score, 75)

    def test_explain_name_score_keeps_fuzzy_diagnostic_available(self):
        """Verifie le diagnostic fuzzy quand aucune regle metier ne rejette.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la regle de score.
        """

        result = self.service.explain_name_score(
            "Legend of Zelda",
            "The Legend of Zelda",
        )

        self.assertGreaterEqual(result.score, 75)
        self.assertEqual("scored", result.decision.value)
        self.assertEqual("fuzzy_similarity", result.rule)

    def test_find_existing_game_id_accepts_equivalent_hyphenated_arabic_and_roman_suffixes(self):
        """Verifie le matching d'une suite a suffixe compose equivalent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le rattachement de la meme suite.
        """

        game = CollectionImportGame("Final Fantasy X-2", "PS2", None, None)
        existing_game_ids = {("ps2", "final fantasy 10-2"): 17}

        result = self.service.evaluate_existing_game(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_ids),
        )

        self.assertEqual(17, result.existing_game_id)
        self.assertEqual(100, result.best_candidate.score)

    def test_platform_index_limits_fuzzy_candidates_to_imported_platform(self):
        """Verifie que le score fuzzy ne parcourt que la plateforme demandee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les comparaisons effectuees.
        """

        scored_candidates = []
        game = CollectionImportGame("Legend of Zelda", "Switch", None, None)
        existing_game_ids = {
            ("switch", "the legend of zelda"): 11,
            ("nes", "legend of zelda"): 13,
        }
        original_matching_score = self.service._matching_score
        self.service._matching_score = lambda imported_key, candidate_key: (
            scored_candidates.append(candidate_key)
            or original_matching_score(imported_key, candidate_key)
        )

        game_id = self.service.find_existing_game_id(
            game,
            existing_game_ids,
            self.service.build_platform_index(existing_game_ids),
        )

        self.assertEqual(11, game_id)
        self.assertEqual(["the legend of zelda"], scored_candidates)

    def test_evaluate_existing_game_returns_best_candidate_when_created(self):
        """Verifie le meilleur candidat quand aucun rattachement n'est accepte.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le score de diagnostic.
        """

        game = CollectionImportGame("Zelda", "Switch", None, None)
        existing_game_references = {
            ("switch", "mario kart"): (17, "Mario Kart"),
            ("nes", "zelda"): (19, "Zelda NES"),
        }

        result = self.service.evaluate_existing_game(
            game,
            {
                game_key: game_reference[0]
                for game_key, game_reference in existing_game_references.items()
            },
            self.service.build_platform_index(existing_game_references),
        )

        self.assertIsNone(result.existing_game_id)
        self.assertEqual("Mario Kart", result.best_candidate.game_name)
        self.assertGreaterEqual(result.best_candidate.score, 0)


if __name__ == "__main__":
    unittest.main()
