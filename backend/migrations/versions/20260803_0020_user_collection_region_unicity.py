#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-08-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : unicite des exemplaires utilisateur par jeu et region.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260803_0020"
down_revision: Union[str, None] = "20260729_0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


REGION_CHECK_SQL = (
    "region IN ('JAP','US','EU-FR','EU-UK','EU-DE','EU-ES','EU-IT',"
    "'AU','ASIA','KOR','TWN','HK','CHN')"
)
LEGACY_REGION_CHECK_SQL = (
    "region IS NULL OR region IN ('JAP','US','EU-FR','EU-UK','EU-DE','EU-ES',"
    "'EU-IT','AU','ASIA','KOR','TWN','HK','CHN')"
)


def upgrade() -> None:
    """Ajoute la region a la cle primaire des collections utilisateur.

    Args:
        Aucun.

    Returns:
        None: La fonction applique la migration.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_constraint(
        "ck_t_user_collection_region",
        "t_user_collection",
        type_="check",
        schema=schema_name,
    )
    op.execute(
        sa.text(
            f'UPDATE "{schema_name}".t_user_collection '
            "SET region = 'EU-FR' WHERE region IS NULL OR region = ''"
        )
    )
    op.alter_column(
        "t_user_collection",
        "region",
        nullable=False,
        server_default=sa.text("'EU-FR'"),
        existing_type=sa.String(length=8),
        schema=schema_name,
    )
    op.drop_constraint(
        "t_user_collection_pkey",
        "t_user_collection",
        type_="primary",
        schema=schema_name,
    )
    op.create_primary_key(
        "t_user_collection_pkey",
        "t_user_collection",
        ["user_id", "game_id", "region"],
        schema=schema_name,
    )
    op.create_check_constraint(
        "ck_t_user_collection_region",
        "t_user_collection",
        REGION_CHECK_SQL,
        schema=schema_name,
    )


def downgrade() -> None:
    """Retire la region de la cle primaire des collections utilisateur.

    Args:
        Aucun.

    Returns:
        None: La fonction annule la migration.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_constraint(
        "ck_t_user_collection_region",
        "t_user_collection",
        type_="check",
        schema=schema_name,
    )
    op.drop_constraint(
        "t_user_collection_pkey",
        "t_user_collection",
        type_="primary",
        schema=schema_name,
    )
    op.execute(
        sa.text(
            f'DELETE FROM "{schema_name}".t_user_collection kept '
            "USING ("
            "SELECT ctid, ROW_NUMBER() OVER ("
            "PARTITION BY user_id, game_id ORDER BY region"
            ") AS row_number "
            f'FROM "{schema_name}".t_user_collection'
            ") ranked "
            "WHERE kept.ctid = ranked.ctid AND ranked.row_number > 1"
        )
    )
    op.alter_column(
        "t_user_collection",
        "region",
        nullable=True,
        server_default=None,
        existing_type=sa.String(length=8),
        schema=schema_name,
    )
    op.create_primary_key(
        "t_user_collection_pkey",
        "t_user_collection",
        ["user_id", "game_id"],
        schema=schema_name,
    )
    op.create_check_constraint(
        "ck_t_user_collection_region",
        "t_user_collection",
        LEGACY_REGION_CHECK_SQL,
        schema=schema_name,
    )
