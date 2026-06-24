#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-24
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : politique d'acces aux collections partagees pour les invites.

from dataclasses import dataclass, replace
from typing import Any

from services.auth import UserProfile

from .user_collection_query_contract import (
    UserCollectionGameQueryCriteria,
    UserCollectionPlatformQueryCriteria,
)


@dataclass(frozen=True)
class CollectionAccessContext:
    """Decrit la collection cible et les droits de lecture courants.

    Attributes:
        user_id (int): Identifiant du proprietaire de la collection cible.
        is_guest (bool): Indique si la lecture vient d'une session invitee.
        allow_collection (bool): Autorisation de lire les jeux possedes.
        allow_wishlist (bool): Autorisation de lire la liste de souhaits.
        allow_prices (bool): Autorisation de lire les informations de prix.
    """

    user_id: int
    is_guest: bool
    allow_collection: bool = True
    allow_wishlist: bool = True
    allow_prices: bool = True


class GuestCollectionAccessPolicy:
    """Applique le perimetre et le masquage d'une session GUEST."""

    PRICE_FIELDS = ("purchase_price", "price_unit")
    PRICE_STATISTIC_FIELDS = ("total_value", "average_value")

    def create_context(self, payload: dict[str, Any], user_id_resolver) -> CollectionAccessContext:
        """Construit le contexte de lecture depuis le token valide.

        Args:
            payload (dict[str, Any]): Claims du Bearer valide.
            user_id_resolver (Callable[[str], int | None]): Resolution d'un USER par email.

        Returns:
            CollectionAccessContext: Collection cible et permissions applicables.

        Raises:
            ValueError: Si l'identite ou les claims GUEST sont invalides.
        """

        if UserProfile.normalize(payload.get("profile")) is UserProfile.GUEST:
            permissions = payload.get("permissions")
            if not isinstance(permissions, dict):
                raise ValueError("Permissions de la session invitee invalides.")
            owner_user_id = self._positive_identifier(payload.get("owner_user_id"))
            return CollectionAccessContext(
                user_id=owner_user_id,
                is_guest=True,
                allow_collection=permissions.get("collection") is True,
                allow_wishlist=permissions.get("wishlist") is True,
                allow_prices=permissions.get("prices") is True,
            )

        subject = str(payload.get("sub") or "").strip().lower()
        if not subject:
            raise ValueError("Utilisateur connecte invalide.")
        user_id = user_id_resolver(subject)
        if user_id is None:
            raise ValueError("Utilisateur connecte introuvable.")
        return CollectionAccessContext(user_id=int(user_id), is_guest=False)

    def scope_criteria(
        self,
        context: CollectionAccessContext,
        criteria: UserCollectionPlatformQueryCriteria | UserCollectionGameQueryCriteria,
    ) -> UserCollectionPlatformQueryCriteria | UserCollectionGameQueryCriteria:
        """Impose aux recherches GUEST une categorie explicitement autorisee.

        Args:
            context (CollectionAccessContext): Droits de lecture courants.
            criteria (UserCollectionPlatformQueryCriteria | UserCollectionGameQueryCriteria): Criteres demandes.

        Returns:
            UserCollectionPlatformQueryCriteria | UserCollectionGameQueryCriteria: Criteres securises.

        Raises:
            PermissionError: Si la categorie demandee n'est pas accordee.
        """

        if not context.is_guest:
            return criteria
        if criteria.wishlist is not None:
            self.ensure_category_allowed(context, criteria.wishlist)
            return criteria
        if context.allow_collection and context.allow_wishlist:
            return criteria
        if context.allow_collection:
            return replace(criteria, wishlist=False)
        if context.allow_wishlist:
            return replace(criteria, wishlist=True)
        raise PermissionError("Aucune categorie de collection n'est autorisee.")

    def ensure_category_allowed(
        self,
        context: CollectionAccessContext,
        wishlist: bool,
    ) -> None:
        """Verifie le droit GUEST sur une categorie collection.

        Args:
            context (CollectionAccessContext): Droits de lecture courants.
            wishlist (bool): `True` pour la wishlist, sinon la collection.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            PermissionError: Si la categorie n'est pas accordee.
        """

        if not context.is_guest:
            return
        is_allowed = context.allow_wishlist if wishlist else context.allow_collection
        if not is_allowed:
            category = "wishlist" if wishlist else "collection"
            raise PermissionError(f"Acces a la categorie {category} non autorise.")

    def filter_games(self, context: CollectionAccessContext, payload: dict[str, Any]) -> dict[str, Any]:
        """Retire les prix interdits d'une liste de jeux.

        Args:
            context (CollectionAccessContext): Droits de lecture courants.
            payload (dict[str, Any]): Reponse paginee de jeux.

        Returns:
            dict[str, Any]: Reponse filtree sans mutation de l'originale.

        Raises:
            Aucun.
        """

        result = dict(payload)
        result["games"] = [self.filter_game(context, game) for game in payload.get("games", [])]
        return result

    def filter_platforms(
        self,
        context: CollectionAccessContext,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Force a zero les statistiques de prix par plateforme interdites.

        Args:
            context (CollectionAccessContext): Droits de lecture courants.
            payload (dict[str, Any]): Reponse paginee de plateformes.

        Returns:
            dict[str, Any]: Reponse filtree sans mutation de l'originale.

        Raises:
            Aucun.
        """

        if not context.is_guest or context.allow_prices:
            return payload
        result = dict(payload)
        result["platforms"] = []
        for platform in payload.get("platforms", []):
            filtered_platform = dict(platform)
            self._clear_price_statistics(filtered_platform)
            result["platforms"].append(filtered_platform)
        return result

    def filter_game(self, context: CollectionAccessContext, game: dict[str, Any]) -> dict[str, Any]:
        """Retire les prix interdits d'un detail de jeu.

        Args:
            context (CollectionAccessContext): Droits de lecture courants.
            game (dict[str, Any]): Jeu serialise par le service de collection.

        Returns:
            dict[str, Any]: Jeu filtre sans mutation de l'original.

        Raises:
            Aucun.
        """

        result = dict(game)
        if context.is_guest and not context.allow_prices:
            for field_name in self.PRICE_FIELDS:
                result.pop(field_name, None)
        return result

    def filter_statistics(
        self,
        context: CollectionAccessContext,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Force les statistiques de prix a zero lorsqu'elles sont interdites.

        Args:
            context (CollectionAccessContext): Droits de lecture courants.
            payload (dict[str, Any]): Statistiques globales et par categorie.

        Returns:
            dict[str, Any]: Statistiques filtrees sans mutation de l'original.

        Raises:
            Aucun.
        """

        if not context.is_guest or context.allow_prices:
            return payload
        result = dict(payload)
        self._clear_price_statistics(result)
        for category in ("collection", "wishlist"):
            if isinstance(result.get(category), dict):
                result[category] = dict(result[category])
                self._clear_price_statistics(result[category])
        return result

    @staticmethod
    def _positive_identifier(value: Any) -> int:
        try:
            identifier = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Proprietaire de partage invalide.") from exc
        if identifier <= 0:
            raise ValueError("Proprietaire de partage invalide.")
        return identifier

    def _clear_price_statistics(self, statistics: dict[str, Any]) -> None:
        for field_name in self.PRICE_STATISTIC_FIELDS:
            statistics[field_name] = 0
