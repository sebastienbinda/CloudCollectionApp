#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : environnement Alembic programme par le service database.

from alembic import context
from services.database import DatabaseModelBase

config = context.config
target_metadata = DatabaseModelBase.metadata


def run_migrations_online() -> None:
    """Execute les migrations Alembic avec la connexion fournie par le service.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    connectable = config.attributes.get("connection")
    schema_name = config.attributes.get("schema_name")
    if connectable is None:
        raise RuntimeError("Une connexion SQLAlchemy est requise pour executer Alembic.")
    if not schema_name:
        raise RuntimeError("Le nom du schema est requis pour executer Alembic.")
    target_metadata.schema = schema_name

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=schema_name,
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations(schema_name=schema_name)


run_migrations_online()
