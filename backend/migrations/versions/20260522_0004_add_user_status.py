#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-22
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute le statut fonctionnel des utilisateurs."""

from typing import Sequence, Union

from alembic import op


revision: str = "20260522_0004"
down_revision: Union[str, None] = "20260522_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la colonne `status` a `t_user`.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(
        f"""
        ALTER TABLE "{schema_name}".t_user
        ADD COLUMN IF NOT EXISTS status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
        """
    )
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                JOIN pg_namespace ON pg_namespace.oid = pg_constraint.connamespace
                WHERE conname = 'ck_t_user_status'
                AND nspname = '{schema_name}'
            ) THEN
                ALTER TABLE "{schema_name}".t_user
                ADD CONSTRAINT ck_t_user_status
                CHECK (status IN ('ACTIVE', 'LOCKED'));
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Supprime la colonne `status` de `t_user`.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(
        f"""
        ALTER TABLE "{schema_name}".t_user
        DROP CONSTRAINT IF EXISTS ck_t_user_status,
        DROP COLUMN IF EXISTS status
        """
    )
