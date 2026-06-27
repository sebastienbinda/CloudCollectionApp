#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute la gestion des signalements et corrections de doublons de jeux."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260627_0016"
down_revision: Union[str, None] = "20260625_0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute le flag de doublon et la table des alias de jeux.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(sa.schema.CreateSequence(sa.Sequence("s_game_alias", schema=schema_name)))
    op.add_column(
        "t_game",
        sa.Column(
            "duplicate_flag",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        schema=schema_name,
    )
    op.create_table(
        "t_game_alias",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name, "s_game_alias")),
            nullable=False,
        ),
        sa.Column("game_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], [f"{schema_name}.t_game.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "name", name="uq_t_game_alias_game_name"),
        schema=schema_name,
    )
    op.create_index(
        "ix_t_game_alias_game_id",
        "t_game_alias",
        ["game_id"],
        schema=schema_name,
    )


def downgrade() -> None:
    """Retire la gestion des doublons de jeux.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_index("ix_t_game_alias_game_id", table_name="t_game_alias", schema=schema_name)
    op.drop_table("t_game_alias", schema=schema_name)
    op.drop_column("t_game", "duplicate_flag", schema=schema_name)
    op.execute(sa.schema.DropSequence(sa.Sequence("s_game_alias", schema=schema_name)))


def _next_sequence_value(schema_name: str, sequence_name: str) -> str:
    """Construit l'appel SQL `nextval` pour une sequence du schema.

    Args:
        schema_name (str): Nom du schema PostgreSQL cible.
        sequence_name (str): Nom de la sequence PostgreSQL.

    Returns:
        str: Expression SQL de valeur par defaut.
    """

    return f"nextval('\"{schema_name}\".\"{sequence_name}\"'::regclass)"
