#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-07-08
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : ajout de la note normalisee aux collections utilisateur.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_0018"
down_revision: Union[str, None] = "20260628_0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la note normalisee aux collections utilisateur.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_user_collection",
        sa.Column("grade_normalized", sa.Integer(), nullable=True),
        schema=schema_name,
    )


def downgrade() -> None:
    """Supprime la note normalisee des collections utilisateur.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_column("t_user_collection", "grade_normalized", schema=schema_name)
