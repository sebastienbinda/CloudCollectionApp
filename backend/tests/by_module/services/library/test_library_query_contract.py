#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests unitaires du contrat de requete Bibliotheque.

import unittest

from services.library import LibraryQueryParser, LibrarySortRule


class FakeQueryParameters:
    """Simule les parametres HTTP repetables de Flask."""

    def __init__(self, values=None):
        """Initialise les parametres factices.

        Args:
            values (dict | None): Valeurs brutes par nom de parametre.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.values = values or {}

    def get(self, key, default=None):
        """Retourne la premiere valeur d'un parametre.

        Args:
            key (str): Nom du parametre.
            default (object | None): Valeur par defaut.

        Returns:
            object | None: Premiere valeur trouvee.
        """

        value = self.values.get(key, default)
        if isinstance(value, list):
            return value[0] if value else default
        return value

    def getlist(self, key):
        """Retourne toutes les valeurs d'un parametre.

        Args:
            key (str): Nom du parametre.

        Returns:
            list: Valeurs trouvees.
        """

        value = self.values.get(key, [])
        if isinstance(value, list):
            return value
        return [value]


class LibraryQueryParserTest(unittest.TestCase):
    """Valide le parsing des criteres de consultation Bibliotheque."""

    def setUp(self):
        """Prepare le parseur teste.

        Args:
            Aucun.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.parser = LibraryQueryParser()

    def test_parse_defaults_when_query_parameters_are_missing(self):
        """Verifie les valeurs par defaut sans parametres.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les fallbacks.
        """

        criteria = self.parser.parse("platforms", {})

        self.assertEqual(0, criteria.page_request.page)
        self.assertEqual(500, criteria.page_request.size)
        self.assertEqual(0, criteria.page_request.offset)
        self.assertEqual("", criteria.name)
        self.assertEqual("", criteria.normalized_name)
        self.assertEqual((LibrarySortRule("name", "asc"),), criteria.sort_rules)

    def test_parse_falls_back_for_invalid_pagination_values(self):
        """Verifie les fallbacks de pagination invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs normalisees.
        """

        invalid_examples = [
            {"page": "-1", "size": "10"},
            {"page": "bad", "size": "bad"},
            {"page": "2", "size": "-1"},
            {"page": "2", "size": "0"},
            {"page": "2", "size": "501"},
        ]

        parsed_values = [
            self.parser.parse("platforms", example).page_request
            for example in invalid_examples
        ]

        self.assertEqual((0, 10), (parsed_values[0].page, parsed_values[0].size))
        self.assertEqual((0, 500), (parsed_values[1].page, parsed_values[1].size))
        self.assertEqual((2, 500), (parsed_values[2].page, parsed_values[2].size))
        self.assertEqual((2, 500), (parsed_values[3].page, parsed_values[3].size))
        self.assertEqual((2, 500), (parsed_values[4].page, parsed_values[4].size))

    def test_parse_normalizes_name_filter_without_case_or_accents(self):
        """Verifie la normalisation du filtre `name`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nom brut et le nom normalise.
        """

        criteria = self.parser.parse("games", {"name": "  École du Jeu  "})

        self.assertEqual("École du Jeu", criteria.name)
        self.assertEqual("ecole du jeu", criteria.normalized_name)

    def test_parse_normalizes_platform_filter_without_case_or_accents(self):
        """Verifie la normalisation du filtre `platform`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la plateforme brute et normalisee.
        """

        criteria = self.parser.parse("games", {"platform": "  Méga Drive  "})

        self.assertEqual("Méga Drive", criteria.platform)
        self.assertEqual("mega drive", criteria.normalized_platform)

    def test_parse_accepts_duplicate_flag_filter(self):
        """Verifie le parsing du filtre de jeux signales comme doublons.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les valeurs booleennes.
        """

        flagged_criteria = self.parser.parse("games", {"duplicate_flag": "true"})
        unflagged_criteria = self.parser.parse("games", {"duplicate_flag": "false"})
        ignored_criteria = self.parser.parse("games", {"duplicate_flag": "all"})

        self.assertTrue(flagged_criteria.duplicate_flag)
        self.assertFalse(unflagged_criteria.duplicate_flag)
        self.assertIsNone(ignored_criteria.duplicate_flag)

    def test_parse_accepts_game_validation_status_filter(self):
        """Verifie le parsing du filtre admin de statut de validation jeu.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les statuts autorises.
        """

        waiting_criteria = self.parser.parse("games", {"status": "waiting_validation"})
        accepted_criteria = self.parser.parse("games", {"status": "ACCEPTED"})
        ignored_criteria = self.parser.parse("games", {"status": "refused"})

        self.assertEqual("WAITING_VALIDATION", waiting_criteria.status)
        self.assertEqual("ACCEPTED", accepted_criteria.status)
        self.assertEqual("", ignored_criteria.status)

    def test_filtered_validation_status_is_admin_only(self):
        """Verifie que le filtre statut ne s'applique qu'aux administrateurs.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la protection du filtre.
        """

        public_criteria = self.parser.parse("games", {"status": "WAITING_VALIDATION"})
        admin_criteria = self.parser.parse(
            "games",
            {"status": "WAITING_VALIDATION"},
            requester_profile="ADMIN",
        )

        self.assertEqual("", public_criteria.filtered_validation_status)
        self.assertEqual("WAITING_VALIDATION", admin_criteria.filtered_validation_status)

    def test_parse_accepts_multiple_sort_parameters(self):
        """Verifie le parsing de plusieurs tris autorises.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident les regles de tri.
        """

        criteria = self.parser.parse(
            "games",
            FakeQueryParameters({"sort": ["release_date,desc", "developer,ASC"]}),
        )

        self.assertEqual(
            (
                LibrarySortRule("release_date", "desc"),
                LibrarySortRule("developer", "asc"),
            ),
            criteria.sort_rules,
        )

    def test_parse_accepts_platform_end_date_sort(self):
        """Verifie que les plateformes peuvent etre triees par date de retrait.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la colonne de tri.
        """

        criteria = self.parser.parse("platforms", {"sort": "end_date,desc"})

        self.assertEqual((LibrarySortRule("end_date", "desc"),), criteria.sort_rules)

    def test_parse_rejects_sort_columns_outside_entity_allowlist(self):
        """Verifie qu'une colonne non autorisee retombe sur `name,asc`.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la securisation de la colonne.
        """

        criteria = self.parser.parse("platforms", {"sort": "developer,desc"})

        self.assertEqual((LibrarySortRule("name", "asc"),), criteria.sort_rules)

    def test_parse_falls_back_to_ascending_for_invalid_sort_direction(self):
        """Verifie le fallback du sens de tri invalide.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le sens de tri.
        """

        criteria = self.parser.parse("studios", {"sort": "country,sideways"})

        self.assertEqual((LibrarySortRule("country", "asc"),), criteria.sort_rules)

    def test_parse_uses_default_sort_for_unknown_entity(self):
        """Verifie le fallback lorsqu'une entite inconnue est demandee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le tri par defaut.
        """

        criteria = self.parser.parse("unknown", {"sort": "name,desc"})

        self.assertEqual((LibrarySortRule("name", "asc"),), criteria.sort_rules)


if __name__ == "__main__":
    unittest.main()
