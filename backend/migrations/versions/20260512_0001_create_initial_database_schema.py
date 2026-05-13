#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Cree le schema SQL initial de CloudCollectionApp."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260512_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cree les tables et sequences initiales dans le schema cible.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    _create_sequences(schema_name)
    _create_tables(schema_name)


def downgrade() -> None:
    """Supprime les tables et sequences initiales du schema cible.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    for table_name in (
        "t_user_collection",
        "t_game",
        "t_user",
        "t_studio",
        "t_platform",
        "t_schema_version",
    ):
        op.drop_table(table_name, schema=schema_name)
    for sequence_name in ("s_user", "s_game", "s_studio", "s_platform"):
        op.execute(sa.schema.DropSequence(sa.Sequence(sequence_name, schema=schema_name)))


def _create_sequences(schema_name: str) -> None:
    """Cree les sequences declarees dans le schema de reference.

    Args:
        schema_name (str): Nom du schema PostgreSQL cible.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    for sequence_name in ("s_platform", "s_game", "s_studio", "s_user"):
        op.execute(sa.schema.CreateSequence(sa.Sequence(sequence_name, schema=schema_name)))


def _create_tables(schema_name: str) -> None:
    """Cree les tables declarees dans `db-schema.md`.

    Args:
        schema_name (str): Nom du schema PostgreSQL cible.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    op.create_table(
        "t_schema_version",
        sa.Column("version", sa.String(length=5), nullable=False),
        sa.Column("date_creation", sa.DateTime(), nullable=False),
        sa.Column("update_date", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("version"),
        schema=schema_name,
    )
    op.create_table(
        "t_platform",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name, "s_platform")),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("release_date", sa.DateTime(), nullable=True),
        sa.Column("manufacturer", sa.String(length=128), nullable=True),
        sa.Column("description", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=schema_name,
    )
    op.create_table(
        "t_studio",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name, "s_studio")),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("country", sa.String(length=256), nullable=True),
        sa.Column("city", sa.String(length=256), nullable=True),
        sa.Column("creation_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_t_studio_name"),
        schema=schema_name,
    )
    op.create_table(
        "t_user",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name, "s_user")),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=256), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("is_email_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("email_verification_token_hash", sa.String(length=64), nullable=True),
        sa.Column("email_verification_expires_at", sa.DateTime(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.Column("last_connexion_date", sa.DateTime(), nullable=True),
        sa.Column("collection_file_path", sa.String(length=512), nullable=True),
        sa.Column("collection_file_description", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_t_user_email"),
        schema=schema_name,
    )
    op.create_table(
        "t_game",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name, "s_game")),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("release_date", sa.DateTime(), nullable=True),
        sa.Column("developper", sa.BigInteger(), nullable=True),
        sa.Column("editor", sa.BigInteger(), nullable=True),
        sa.Column("platform", sa.BigInteger(), nullable=False),
        sa.Column("description", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["developper"], [f"{schema_name}.t_studio.id"]),
        sa.ForeignKeyConstraint(["editor"], [f"{schema_name}.t_studio.id"]),
        sa.ForeignKeyConstraint(["platform"], [f"{schema_name}.t_platform.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "platform", name="uq_t_game_name_platform"),
        schema=schema_name,
    )
    op.create_table(
        "t_user_collection",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("game_id", sa.BigInteger(), nullable=False),
        sa.Column("game_additional_name", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], [f"{schema_name}.t_user.id"]),
        sa.ForeignKeyConstraint(["game_id"], [f"{schema_name}.t_game.id"]),
        sa.PrimaryKeyConstraint("user_id", "game_id"),
        schema=schema_name,
    )


def _next_sequence_value(schema_name: str, sequence_name: str) -> str:
    """Construit l'appel PostgreSQL `nextval` pour une sequence du schema.

    Args:
        schema_name (str): Nom du schema PostgreSQL cible.
        sequence_name (str): Nom de la sequence cible.

    Returns:
        str: Expression SQL utilisee comme valeur par defaut.
    """

    return f"nextval('\"{schema_name}\".\"{sequence_name}\"'::regclass)"
