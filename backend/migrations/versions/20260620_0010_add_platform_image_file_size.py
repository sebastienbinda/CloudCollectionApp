#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute la taille stockee des images de plateformes."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260620_0010"
down_revision: Union[str, None] = "20260618_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la colonne de taille des fichiers image.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_platform_image",
        sa.Column(
            "file_size_bytes",
            sa.BigInteger(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        schema=schema_name,
    )
    op.create_check_constraint(
        "ck_t_platform_image_file_size_bytes",
        "t_platform_image",
        "file_size_bytes >= 0",
        schema=schema_name,
    )
    op.alter_column(
        "t_platform_image",
        "file_size_bytes",
        server_default=None,
        schema=schema_name,
    )


def downgrade() -> None:
    """Supprime la colonne de taille des fichiers image.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_constraint(
        "ck_t_platform_image_file_size_bytes",
        "t_platform_image",
        type_="check",
        schema=schema_name,
    )
    op.drop_column("t_platform_image", "file_size_bytes", schema=schema_name)
