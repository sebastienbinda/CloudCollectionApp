#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : ajout du stockage des partages temporaires de collection.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260623_0014"
down_revision: Union[str, None] = "20260622_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cree la table des partages temporaires de collection.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(sa.schema.CreateSequence(sa.Sequence("s_collection_share", schema=schema_name)))
    op.create_table(
        "t_collection_share",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name)),
            nullable=False,
        ),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("allow_collection", sa.Boolean(), nullable=False),
        sa.Column("allow_wishlist", sa.Boolean(), nullable=False),
        sa.Column("allow_prices", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "expires_at > created_at",
            name="ck_t_collection_share_expiration",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            [f"{schema_name}.t_user.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=schema_name,
    )
    op.create_index(
        "ix_t_collection_share_owner_user_id",
        "t_collection_share",
        ["owner_user_id"],
        schema=schema_name,
    )


def downgrade() -> None:
    """Supprime le stockage des partages temporaires de collection.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_index(
        "ix_t_collection_share_owner_user_id",
        table_name="t_collection_share",
        schema=schema_name,
    )
    op.drop_table("t_collection_share", schema=schema_name)
    op.execute(sa.schema.DropSequence(sa.Sequence("s_collection_share", schema=schema_name)))


def _next_sequence_value(schema_name: str) -> str:
    """Construit l'expression PostgreSQL de la sequence de partage.

    Args:
        schema_name (str): Nom du schema PostgreSQL.

    Returns:
        str: Expression `nextval` qualifiee.
    """

    return f"nextval('\"{schema_name}\".s_collection_share'::regclass)"
