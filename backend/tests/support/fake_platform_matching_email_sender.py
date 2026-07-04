#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-14
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : expediteur email factice pour les tests de matching plateformes.


class FakePlatformMatchingEmailSender:
    """Capture les emails de verification manuelle des plateformes."""

    def __init__(self):
        """Initialise l'expediteur factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.sent_emails = []

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        content_subtype: str = "plain",
    ) -> None:
        """Memorise un email envoye.

        Args:
            recipient_email (str): Adresse destinataire.
            subject (str): Sujet de l'email.
            body (str): Corps texte.
            content_subtype (str): Sous-type MIME du contenu.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.sent_emails.append(
            {
                "recipient_email": recipient_email,
                "subject": subject,
                "body": body,
                "content_subtype": content_subtype,
            }
        )
