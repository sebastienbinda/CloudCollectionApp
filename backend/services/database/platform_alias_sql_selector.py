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
# Description : fragment SQL de selection d'un alias courant de plateforme.


class PlatformAliasSqlSelector:
    """Construit le fragment SQL de selection d'un alias courant."""

    @staticmethod
    def common_alias_subquery(schema_name: str, platform_id_expression: str) -> str:
        """Retourne une sous-requete SQL selectionnant l'alias courant d'une plateforme.

        Args:
            schema_name (str): Nom du schema PostgreSQL cible.
            platform_id_expression (str): Expression SQL identifiant la plateforme.

        Returns:
            str: Sous-requete SQL retournant un nom d'alias ou `NULL`.

        Raises:
            Aucun.
        """

        return (
            "(SELECT platform_alias.name "
            f'FROM "{schema_name}".t_platform_alias platform_alias '
            f"WHERE platform_alias.platform = {platform_id_expression} "
            "ORDER BY "
            "CASE LOWER(COALESCE(platform_alias.category, '')) "
            "WHEN 'nom_court' THEN 0 "
            "WHEN 'abreviation' THEN 1 "
            "WHEN 'nom_alternatif' THEN 2 "
            "ELSE 3 END, "
            "CASE "
            "WHEN LOWER(COALESCE(platform_alias.usage_region, '')) LIKE 'europe%' THEN 0 "
            "WHEN LOWER(COALESCE(platform_alias.usage_region, '')) = 'international' THEN 1 "
            "ELSE 2 END, "
            "platform_alias.name "
            "LIMIT 1)"
        )
