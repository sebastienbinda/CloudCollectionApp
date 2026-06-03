#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : politique de resolution des doublons wishlist.

from .collection_file_description import WishlistImportMode


class WishlistDuplicatePolicy:
    """Formalise la priorite wishlist lors de doublons d'import."""

    def resolve_wishlist_value(
        self,
        mode: WishlistImportMode,
        existing_wishlist: bool,
        candidate_wishlist: bool,
    ) -> bool:
        """Retourne la valeur wishlist a conserver pour un doublon.

        Args:
            mode (WishlistImportMode): Mode wishlist de l'import courant.
            existing_wishlist (bool): Valeur deja conservee pour le jeu.
            candidate_wishlist (bool): Valeur lue sur le doublon candidat.

        Returns:
            bool: Valeur wishlist finale a conserver.

        Raises:
            Aucun.
        """

        if mode == WishlistImportMode.COLUMN:
            return existing_wishlist or candidate_wishlist
        if mode == WishlistImportMode.SHEET:
            return existing_wishlist and candidate_wishlist
        return False
