#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | |__| (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-07-09
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du selecteur SQL d'alias courant de plateforme.

import unittest

from services.database.platform_alias_sql_selector import PlatformAliasSqlSelector


class PlatformAliasSqlSelectorTest(unittest.TestCase):
    """Valide la selection SQL de l'alias principal de plateforme."""

    def test_common_alias_subquery_prioritizes_europe_before_international_and_other_regions(self):
        """Verifie que les alias europeens sont tries avant les alias internationaux.

        Args:
            Aucun.

        Returns:
            None: Ce test ne retourne aucune valeur.

        Raises:
            AssertionError: Si la priorite regionale SQL n'est pas respectee.
        """

        subquery = PlatformAliasSqlSelector.common_alias_subquery("collection", "platform.id")

        self.assertIn("LIKE 'europe%' THEN 0", subquery)
        self.assertIn("= 'international' THEN 1", subquery)
        self.assertIn("ELSE 2 END", subquery)
        self.assertLess(
            subquery.index("LIKE 'europe%' THEN 0"),
            subquery.index("= 'international' THEN 1"),
        )
        self.assertLess(
            subquery.index("= 'international' THEN 1"),
            subquery.index("ELSE 2 END"),
        )

