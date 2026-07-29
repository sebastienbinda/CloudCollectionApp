#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-07-29
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : ajout du statut de validation aux jeux de la Bibliotheque.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260729_0019"
down_revision: Union[str, None] = "20260708_0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute le statut de validation aux jeux de la Bibliotheque.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_game",
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'ACCEPTED'"),
            nullable=False,
        ),
        schema=schema_name,
    )
    op.create_check_constraint(
        "ck_t_game_status",
        "t_game",
        "status IN ('WAITING_VALIDATION', 'ACCEPTED')",
        schema=schema_name,
    )
    op.create_index(
        "ix_t_game_status",
        "t_game",
        ["status"],
        schema=schema_name,
    )


def downgrade() -> None:
    """Retire le statut de validation des jeux de la Bibliotheque.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_index("ix_t_game_status", table_name="t_game", schema=schema_name)
    op.drop_constraint("ck_t_game_status", "t_game", schema=schema_name, type_="check")
    op.drop_column("t_game", "status", schema=schema_name)
