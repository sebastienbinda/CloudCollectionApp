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
    """Ajoute `end_date`, retire `status` et charge les plateformes CSV.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_platform",
        sa.Column("end_date", sa.DateTime(), nullable=True),
        schema=schema_name,
    )
    op.drop_column("t_platform", "status", schema=schema_name)
    PlatformCatalogSeedService(schema_name).seed_from_csv(
        op.get_bind(),
        _catalog_csv_path(),
    )


def downgrade() -> None:
    """Retablit la colonne `status` et retire `end_date`.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
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
