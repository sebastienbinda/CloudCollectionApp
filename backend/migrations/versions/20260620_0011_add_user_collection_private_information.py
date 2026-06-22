#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute les informations privees aux jeux des collections utilisateur."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260620_0011"
down_revision: Union[str, None] = "20260620_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute les colonnes privees nullable a `t_user_collection`.

    Args:
        Aucun.

    Returns:
        None: La fonction applique la migration.
    """

    schema_name = op.get_context().opts["schema_name"]
    columns = (
        sa.Column("purchase_price", sa.BigInteger(), nullable=True),
        sa.Column("price_unit", sa.String(length=3), nullable=True),
        sa.Column("buy_location", sa.String(length=256), nullable=True),
        sa.Column("buy_date", sa.DateTime(), nullable=True),
        sa.Column("grade", sa.String(length=256), nullable=True),
        sa.Column("condition", sa.SmallInteger(), nullable=True),
        sa.Column("has_manual", sa.Boolean(), nullable=True),
        sa.Column("is_collector", sa.Boolean(), nullable=True),
        sa.Column("has_steelbook", sa.Boolean(), nullable=True),
        sa.Column("is_digital", sa.Boolean(), nullable=True),
        sa.Column("region", sa.String(length=8), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    for column in columns:
        op.add_column("t_user_collection", column, schema=schema_name)
    op.create_check_constraint(
        "ck_t_user_collection_condition",
        "t_user_collection",
        "condition IS NULL OR condition BETWEEN 0 AND 4",
        schema=schema_name,
    )
    op.create_check_constraint(
        "ck_t_user_collection_price_unit",
        "t_user_collection",
        "price_unit IS NULL OR price_unit IN ('EUR','USD','GBP','JPY','AUD','CAD','CHF','CNY','KRW')",
        schema=schema_name,
    )
    op.create_check_constraint(
        "ck_t_user_collection_region",
        "t_user_collection",
        "region IS NULL OR region IN ('JAP','US','EU-FR','EU-UK','EU-DE','EU-ES','EU-IT','AU','ASIA','KOR','TWN','HK','CHN')",
        schema=schema_name,
    )


def downgrade() -> None:
    """Supprime les informations privees de `t_user_collection`.

    Args:
        Aucun.

    Returns:
        None: La fonction annule la migration.
    """

    schema_name = op.get_context().opts["schema_name"]
    for constraint_name in (
        "ck_t_user_collection_region",
        "ck_t_user_collection_price_unit",
        "ck_t_user_collection_condition",
    ):
        op.drop_constraint(
            constraint_name,
            "t_user_collection",
            type_="check",
            schema=schema_name,
        )
    for column_name in (
        "description", "region", "is_digital", "has_steelbook", "is_collector",
        "has_manual", "condition", "grade", "buy_date", "buy_location",
        "price_unit", "purchase_price",
    ):
        op.drop_column("t_user_collection", column_name, schema=schema_name)
