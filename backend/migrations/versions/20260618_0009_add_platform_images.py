#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-18
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute le stockage SQL des images de plateformes."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260618_0009"
down_revision: Union[str, None] = "20260614_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cree la table des images proposees pour les plateformes.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(sa.schema.CreateSequence(sa.Sequence("s_platform_image", schema=schema_name)))
    op.create_table(
        "t_platform_image",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name, "s_platform_image")),
            nullable=False,
        ),
        sa.Column("platform", sa.BigInteger(), nullable=False),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.CheckConstraint("type IN ('MAIN', 'OTHER')", name="ck_t_platform_image_type"),
        sa.CheckConstraint(
            "status IN ('WAITING_VALIDATION', 'ACCEPTED')",
            name="ck_t_platform_image_status",
        ),
        sa.ForeignKeyConstraint(["platform"], [f"{schema_name}.t_platform.id"]),
        sa.ForeignKeyConstraint(["user_id"], [f"{schema_name}.t_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema=schema_name,
    )
    op.create_index(
        "ix_t_platform_image_platform",
        "t_platform_image",
        ["platform"],
        schema=schema_name,
    )
    op.create_index(
        "ix_t_platform_image_status",
        "t_platform_image",
        ["status"],
        schema=schema_name,
    )
    op.create_index(
        "ix_t_platform_image_user_id",
        "t_platform_image",
        ["user_id"],
        schema=schema_name,
    )
    op.create_index(
        "uq_t_platform_image_single_main",
        "t_platform_image",
        ["platform"],
        unique=True,
        schema=schema_name,
        postgresql_where=sa.text("type = 'MAIN'"),
    )


def downgrade() -> None:
    """Supprime la table des images de plateformes.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_index(
        "uq_t_platform_image_single_main",
        table_name="t_platform_image",
        schema=schema_name,
    )
    op.drop_index(
        "ix_t_platform_image_user_id",
        table_name="t_platform_image",
        schema=schema_name,
    )
    op.drop_index(
        "ix_t_platform_image_status",
        table_name="t_platform_image",
        schema=schema_name,
    )
    op.drop_index(
        "ix_t_platform_image_platform",
        table_name="t_platform_image",
        schema=schema_name,
    )
    op.drop_table("t_platform_image", schema=schema_name)
    op.execute(sa.schema.DropSequence(sa.Sequence("s_platform_image", schema=schema_name)))


def _next_sequence_value(schema_name: str, sequence_name: str) -> str:
    """Construit l'expression SQL de valeur suivante d'une sequence.

    Args:
        schema_name (str): Nom du schema PostgreSQL.
        sequence_name (str): Nom de la sequence.

    Returns:
        str: Expression SQL `nextval` qualifiee.
    """

    return f"nextval('\"{schema_name}\".{sequence_name}'::regclass)"
