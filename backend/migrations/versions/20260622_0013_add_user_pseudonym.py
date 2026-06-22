#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-22
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : ajout du pseudonyme public unique des utilisateurs.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0013"
down_revision: Union[str, None] = "20260621_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute et initialise le pseudonyme unique des utilisateurs.

    Args:
        Aucun.

    Returns:
        None: La migration derive les pseudonymes depuis les emails existants.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_user",
        sa.Column("pseudonym", sa.String(length=32), nullable=True),
        schema=schema_name,
    )
    op.execute(_backfill_pseudonyms_statement(schema_name))
    op.alter_column("t_user", "pseudonym", nullable=False, schema=schema_name)
    op.execute(
        f'CREATE UNIQUE INDEX uq_t_user_pseudonym_lower '
        f'ON "{schema_name}".t_user (LOWER(pseudonym))'
    )


def downgrade() -> None:
    """Supprime le pseudonyme des utilisateurs.

    Args:
        Aucun.

    Returns:
        None: La fonction restaure le schema precedent.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_index("uq_t_user_pseudonym_lower", table_name="t_user", schema=schema_name)
    op.drop_column("t_user", "pseudonym", schema=schema_name)


def _backfill_pseudonyms_statement(schema_name: str) -> str:
    """Construit le bloc SQL de generation des pseudonymes historiques.

    Args:
        schema_name (str): Schema PostgreSQL cible.

    Returns:
        str: Bloc SQL deterministe avec suffixes en cas de collision.
    """

    return f'''
    DO $$
    DECLARE
        user_row RECORD;
        base_pseudonym TEXT;
        candidate TEXT;
        suffix_number INTEGER;
        suffix_text TEXT;
    BEGIN
        FOR user_row IN SELECT id, email FROM "{schema_name}".t_user ORDER BY id LOOP
            base_pseudonym := regexp_replace(
                split_part(user_row.email, '@', 1),
                '[^A-Za-z0-9_-]+',
                '',
                'g'
            );
            IF length(base_pseudonym) < 3 THEN
                base_pseudonym := 'user';
            END IF;
            base_pseudonym := left(base_pseudonym, 32);
            candidate := base_pseudonym;
            suffix_number := 2;
            WHILE EXISTS (
                SELECT 1 FROM "{schema_name}".t_user
                WHERE pseudonym IS NOT NULL AND lower(pseudonym) = lower(candidate)
            ) LOOP
                suffix_text := '-' || suffix_number::text;
                candidate := left(base_pseudonym, 32 - length(suffix_text)) || suffix_text;
                suffix_number := suffix_number + 1;
            END LOOP;
            UPDATE "{schema_name}".t_user
            SET pseudonym = candidate
            WHERE id = user_row.id;
        END LOOP;
    END $$;
    '''
