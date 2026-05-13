#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-13
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute la validation email aux utilisateurs."""

from typing import Sequence, Union

from alembic import op


revision: str = "20260513_0002"
down_revision: Union[str, None] = "20260512_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute les colonnes de validation email a `t_user`.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = '{schema_name}'
                AND table_name = 't_user'
                AND column_name = 'password_encrypted'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = '{schema_name}'
                AND table_name = 't_user'
                AND column_name = 'password_hash'
            ) THEN
                ALTER TABLE "{schema_name}".t_user
                RENAME COLUMN password_encrypted TO password_hash;
            END IF;
        END $$;
        """
    )
    op.execute(
        f"""
        ALTER TABLE "{schema_name}".t_user
        ADD COLUMN IF NOT EXISTS is_email_verified BOOLEAN NOT NULL DEFAULT false,
        ADD COLUMN IF NOT EXISTS email_verification_token_hash VARCHAR(64),
        ADD COLUMN IF NOT EXISTS email_verification_expires_at TIMESTAMP,
        ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP
        """
    )


def downgrade() -> None:
    """Supprime les colonnes de validation email.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.execute(
        f"""
        ALTER TABLE "{schema_name}".t_user
        DROP COLUMN IF EXISTS email_verified_at,
        DROP COLUMN IF EXISTS email_verification_expires_at,
        DROP COLUMN IF EXISTS email_verification_token_hash,
        DROP COLUMN IF EXISTS is_email_verified
        """
    )
