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
# Description : envoi d'un email de test depuis le conteneur backend.

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_BACKEND_DIR))

from services.email import EmailConfiguration, EmailSenderFactory


def parse_arguments() -> argparse.Namespace:
    """Analyse les arguments de l'email de test.

    Args:
        Aucun.

    Returns:
        argparse.Namespace: Arguments valides du script.
    """

    parser = argparse.ArgumentParser(
        description="Envoie un email de test avec la configuration SMTP du backend."
    )
    parser.add_argument(
        "--to",
        required=True,
        help="Adresse email destinataire du test.",
    )
    parser.add_argument(
        "--subject",
        default="Test email CloudCollectionApp",
        help="Sujet de l'email de test.",
    )
    parser.add_argument(
        "--body",
        default=None,
        help="Corps texte optionnel de l'email de test.",
    )
    return parser.parse_args()


def build_default_body() -> str:
    """Construit le corps par defaut de l'email de test.

    Args:
        Aucun.

    Returns:
        str: Corps texte de test.
    """

    return (
        "Bonjour,\n\n"
        "Ceci est un email de test envoye depuis le conteneur backend "
        "CloudCollectionApp.\n\n"
        f"Date d'envoi: {datetime.now().isoformat(timespec='seconds')}\n"
        f"Mode email: {os.getenv('EMAIL_DELIVERY_MODE', 'console')}\n"
        f"Serveur SMTP: {os.getenv('SMTP_HOST', '')}\n"
    )


def main() -> int:
    """Execute l'envoi de l'email de test.

    Args:
        Aucun.

    Returns:
        int: Code de sortie Unix.
    """

    arguments = parse_arguments()
    try:
        configuration = EmailConfiguration.from_environment()
        email_sender = EmailSenderFactory.create(configuration)
        email_sender.send_email(
            recipient_email=arguments.to,
            subject=arguments.subject,
            body=arguments.body or build_default_body(),
        )
    except Exception as exc:
        print(f"Erreur pendant l'envoi de l'email de test: {exc}", file=sys.stderr)
        return 1

    print(f"Email de test envoye vers {arguments.to}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
