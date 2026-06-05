#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-05
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute le statut utilisateur en attente de validation administrateur."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260605_0007"
down_revision: Union[str, None] = "20260603_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Autorise `WAITING_VALIDATION` dans `t_user.status`.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.alter_column("t_user", "status", type_=sa.String(length=32), schema=schema_name)
    op.drop_constraint("ck_t_user_status", "t_user", schema=schema_name, type_="check")
    op.create_check_constraint(
        "ck_t_user_status",
        "t_user",
        "status IN ('ACTIVE', 'WAITING_VALIDATION', 'LOCKED')",
        schema=schema_name,
    )


def downgrade() -> None:
    """Retire `WAITING_VALIDATION` des statuts autorises.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(
        sa.text(
            f'UPDATE "{schema_name}".t_user '
            "SET status = 'ACTIVE' WHERE status = 'WAITING_VALIDATION'"
        )
    )
    op.drop_constraint("ck_t_user_status", "t_user", schema=schema_name, type_="check")
    op.create_check_constraint(
        "ck_t_user_status",
        "t_user",
        "status IN ('ACTIVE', 'LOCKED')",
        schema=schema_name,
    )
    op.alter_column("t_user", "status", type_=sa.String(length=16), schema=schema_name)
