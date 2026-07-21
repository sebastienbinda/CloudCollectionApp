#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/|_| |_|\___/
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-21
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : synchronisation des donnees filtrees d'un import utilisateur.

from services.collection.imports import CollectionImportData


class CollectionImportDataSynchronizer:
    """Expose les donnees d'import filtrees sur l'objet source."""

    def synchronize(
        self,
        import_data: CollectionImportData,
        matched_import_data: CollectionImportData,
    ) -> None:
        """Copie les donnees rattachees dans l'objet d'import initial.

        Args:
            import_data (CollectionImportData): Donnees initiales lues par le reader.
            matched_import_data (CollectionImportData): Donnees rattachees au catalogue.

        Returns:
            None: L'objet initial est mis a jour pour les traitements suivants.
        """

        object.__setattr__(import_data, "platforms", matched_import_data.platforms)
        object.__setattr__(import_data, "studios", matched_import_data.studios)
        object.__setattr__(import_data, "games", matched_import_data.games)
        object.__setattr__(import_data, "warnings", matched_import_data.warnings)
