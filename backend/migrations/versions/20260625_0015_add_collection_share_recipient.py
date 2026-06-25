#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-25
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : ajout du destinataire lisible aux partages de collection.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260625_0015"
down_revision: Union[str, None] = "20260623_0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute le destinataire optionnel des partages de collection.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_collection_share",
        sa.Column("recipient", sa.String(length=256), nullable=True),
        schema=schema_name,
    )


def downgrade() -> None:
    """Supprime le destinataire optionnel des partages de collection.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_column("t_collection_share", "recipient", schema=schema_name)
