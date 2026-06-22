#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-21
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : migration du prix d'achat vers un decimal a deux chiffres.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260621_0012"
down_revision: Union[str, None] = "20260620_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Autorise deux decimales pour le prix d'achat.

    Args:
        Aucun.

    Returns:
        None: La fonction applique la migration sans modifier les prix existants.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.alter_column(
        "t_user_collection",
        "purchase_price",
        existing_type=sa.BigInteger(),
        type_=sa.Numeric(precision=12, scale=2),
        existing_nullable=True,
        postgresql_using="purchase_price::numeric(12,2)",
        schema=schema_name,
    )


def downgrade() -> None:
    """Restaure un prix entier en arrondissant les valeurs decimales.

    Args:
        Aucun.

    Returns:
        None: La fonction restaure le type entier historique.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.alter_column(
        "t_user_collection",
        "purchase_price",
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.BigInteger(),
        existing_nullable=True,
        postgresql_using="ROUND(purchase_price)::bigint",
        schema=schema_name,
    )
