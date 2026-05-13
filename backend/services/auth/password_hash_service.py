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
# Description : service de hachage non reversible des mots de passe.

from werkzeug.security import generate_password_hash


class PasswordHashService:
    """Produit des empreintes de mots de passe non reversibles.

    Le service s'appuie sur Werkzeug avec `scrypt`, un algorithme adapte au
    stockage de mots de passe et incluant un sel aleatoire par empreinte.
    """

    HASH_METHOD = "scrypt"

    def hash_password(self, password: str) -> str:
        """Hache un mot de passe avant stockage en base de donnees.

        Args:
            password (str): Mot de passe brut recu pendant la requete.

        Returns:
            str: Empreinte non reversible contenant le sel et les parametres.

        Raises:
            ValueError: Si le mot de passe est vide.
        """

        if not password:
            raise ValueError("Le mot de passe est obligatoire.")
        return generate_password_hash(password, method=self.HASH_METHOD)
