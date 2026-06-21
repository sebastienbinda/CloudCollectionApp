#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : configuration generique du seuil de matching des etats importes.

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class ConditionMatchingConfiguration:
    """Configure le score minimal de rattachement d'un etat importe.

    Attributes:
        match_limit (int): Score minimal accepte entre 0 et 100.
    """

    match_limit: int = 60

    @classmethod
    def from_environment(cls) -> "ConditionMatchingConfiguration":
        """Construit et valide la configuration depuis l'environnement.

        Args:
            Aucun.

        Returns:
            ConditionMatchingConfiguration: Configuration validee.

        Raises:
            ValueError: Si `ETAT_MATCH_LIMIT` n'est pas un entier entre 0 et 100.
        """

        raw_value = os.getenv("ETAT_MATCH_LIMIT", "60").strip()
        try:
            configuration = cls(int(raw_value))
        except ValueError as exc:
            raise ValueError("ETAT_MATCH_LIMIT doit etre numerique.") from exc
        configuration.validate()
        return configuration

    def validate(self) -> None:
        """Valide la borne du seuil de matching.

        Args:
            Aucun.

        Returns:
            None: La methode valide uniquement la configuration.

        Raises:
            ValueError: Si le seuil est hors de l'intervalle 0 a 100.
        """

        if not 0 <= self.match_limit <= 100:
            raise ValueError("ETAT_MATCH_LIMIT doit etre entre 0 et 100.")
