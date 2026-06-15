#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute le catalogue applicatif des plateformes."""

from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from services.database.platform_catalog_seed_service import PlatformCatalogSeedService


revision: str = "20260614_0008"
down_revision: Union[str, None] = "20260605_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute le catalogue des plateformes et de leurs alias.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(sa.schema.CreateSequence(sa.Sequence("s_platform_alias", schema=schema_name)))
    op.add_column(
        "t_platform",
        sa.Column("end_date", sa.DateTime(), nullable=True),
        schema=schema_name,
    )
    op.drop_column("t_platform", "status", schema=schema_name)
    op.create_table(
        "t_platform_alias",
        sa.Column(
            "id",
            sa.BigInteger(),
            server_default=sa.text(_next_sequence_value(schema_name, "s_platform_alias")),
            nullable=False,
        ),
        sa.Column("platform", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("usage_region", sa.String(length=128), nullable=True),
        sa.Column("comment", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(["platform"], [f"{schema_name}.t_platform.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "name", name="uq_t_platform_alias_platform_name"),
        schema=schema_name,
    )
    op.create_index(
        "ix_t_platform_alias_platform",
        "t_platform_alias",
        ["platform"],
        schema=schema_name,
    )
    PlatformCatalogSeedService(schema_name).seed_from_csv(
        op.get_bind(),
        _catalog_csv_path(),
        _alias_catalog_csv_path(),
    )


def downgrade() -> None:
    """Retablit la colonne `status` et retire le catalogue des alias.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_index(
        "ix_t_platform_alias_platform",
        table_name="t_platform_alias",
        schema=schema_name,
    )
    op.drop_table("t_platform_alias", schema=schema_name)
    op.execute(sa.schema.DropSequence(sa.Sequence("s_platform_alias", schema=schema_name)))
    op.add_column(
        "t_platform",
        sa.Column(
            "status",
            sa.String(length=16),
            server_default=sa.text("'UNKNOWN'"),
            nullable=False,
        ),
        schema=schema_name,
    )
    op.alter_column("t_platform", "status", server_default=None, schema=schema_name)
    op.drop_column("t_platform", "end_date", schema=schema_name)


def _catalog_csv_path() -> Path:
    """Retourne le chemin du CSV de reference embarque des plateformes.

    Args:
        Aucun.

    Returns:
        Path: Chemin absolu vers le catalogue CSV.
    """

    return Path(__file__).resolve().parents[2] / "services" / "database" / "platform_catalog.csv"


def _alias_catalog_csv_path() -> Path:
    """Retourne le chemin du CSV de reference embarque des alias.

    Args:
        Aucun.

    Returns:
        Path: Chemin absolu vers le catalogue CSV des alias.
    """

    return Path(__file__).resolve().parents[2] / "services" / "database" / "platform_alias_catalog.csv"


def _next_sequence_value(schema_name: str, sequence_name: str) -> str:
    """Construit l'appel SQL `nextval` pour une sequence du schema.

    Args:
        schema_name (str): Nom du schema PostgreSQL cible.
        sequence_name (str): Nom de la sequence PostgreSQL.

    Returns:
        str: Expression SQL de valeur par defaut.
    """

    return f"nextval('\"{schema_name}\".\"{sequence_name}\"'::regclass)"
