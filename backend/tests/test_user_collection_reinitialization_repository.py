#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-07
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : tests du repository de reinitialisation de collection utilisateur.

import unittest

from services.database.user_collection_import_repository import (
    SqlAlchemyUserCollectionImportRepository,
    UserCollectionReinitializationNotFoundError,
    _UserCollectionFileRemover,
)


class FakeTransaction:
    """Transaction SQL factice."""

    def __init__(self, connection):
        """Initialise la transaction factice.

        Args:
            connection (object): Connexion retournee par le contexte.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.connection = connection
        self.rolled_back = False

    def __enter__(self):
        """Retourne la connexion transactionnelle.

        Args:
            Aucun.

        Returns:
            object: Connexion transactionnelle.
        """

        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Memorise le rollback implicite en cas d'erreur.

        Args:
            exc_type (type | None): Type d'exception recue.
            exc_value (Exception | None): Exception recue.
            traceback (object | None): Traceback recu.

        Returns:
            bool: `False` pour propager les exceptions.
        """

        self.rolled_back = exc_type is not None
        return False


class FakeEngine:
    """Engine SQLAlchemy factice exposant `begin`."""

    def __init__(self, transaction):
        """Initialise l'engine factice.

        Args:
            transaction (FakeTransaction): Transaction retournee par `begin`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.transaction = transaction

    def begin(self):
        """Retourne une transaction factice.

        Args:
            Aucun.

        Returns:
            FakeTransaction: Transaction configuree.
        """

        return self.transaction


class FakeUserFileRepository:
    """Repository factice du fichier collection utilisateur."""

    def __init__(self, collection_file_path=""):
        """Initialise le repository factice.

        Args:
            collection_file_path (str): Chemin retourne par le verrou utilisateur.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.collection_file_path = collection_file_path
        self.cleared_users = []

    def lock_user_collection_state(self, connection, user_id):
        """Retourne le chemin collection configure.

        Args:
            connection (object): Connexion transactionnelle ignoree.
            user_id (int): Identifiant utilisateur ignore.

        Returns:
            str: Chemin de collection configure.
        """

        return self.collection_file_path

    def clear_collection_file(self, connection, user_id):
        """Memorise le nettoyage du fichier utilisateur.

        Args:
            connection (object): Connexion transactionnelle ignoree.
            user_id (int): Identifiant utilisateur nettoye.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.cleared_users.append(user_id)


class FakeUserCollectionRepository:
    """Repository factice des associations utilisateur-jeu."""

    def __init__(self, association_count=0, delete_error=None):
        """Initialise le repository factice.

        Args:
            association_count (int): Nombre d'associations configure.
            delete_error (Exception | None): Erreur levee pendant la suppression.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.association_count = association_count
        self.delete_error = delete_error
        self.deleted_users = []

    def count_user_game_associations(self, connection, user_id):
        """Retourne le nombre d'associations configure.

        Args:
            connection (object): Connexion transactionnelle ignoree.
            user_id (int): Identifiant utilisateur ignore.

        Returns:
            int: Nombre d'associations configure.
        """

        return self.association_count

    def delete_user_game_associations(self, connection, user_id):
        """Memorise la suppression ou leve une erreur configuree.

        Args:
            connection (object): Connexion transactionnelle ignoree.
            user_id (int): Identifiant utilisateur nettoye.

        Returns:
            int: Nombre d'associations supprimees.

        Raises:
            Exception: Erreur configuree pour le test.
        """

        self.deleted_users.append(user_id)
        if self.delete_error:
            raise self.delete_error
        return self.association_count


class FakeCollectionFileRemover:
    """Suppresseur de fichier factice."""

    def __init__(self, error=None):
        """Initialise le suppresseur factice.

        Args:
            error (Exception | None): Erreur levee pendant la suppression.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.error = error
        self.deleted_paths = []

    def delete_collection_file(self, collection_file_path):
        """Memorise le chemin supprime ou leve une erreur configuree.

        Args:
            collection_file_path (str): Chemin du fichier supprime.

        Returns:
            None: La methode ne retourne aucune valeur.

        Raises:
            Exception: Erreur configuree pour le test.
        """

        self.deleted_paths.append(collection_file_path)
        if self.error:
            raise self.error


class FakeLogger:
    """Logger factice capturant les warnings."""

    def __init__(self):
        """Initialise le logger factice.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.warnings = []

    def warning(self, message):
        """Capture un warning.

        Args:
            message (str): Message journalise.

        Returns:
            None: La methode ne retourne aucune valeur.
        """

        self.warnings.append(message)


class UserCollectionReinitializationRepositoryTest(unittest.TestCase):
    """Valide la transaction de reinitialisation de collection."""

    def test_reinitialize_collection_cleans_sql_and_file(self):
        """Verifie le nettoyage nominal de la collection.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nettoyage complet.
        """

        repository, transaction, user_file, user_collection, remover = self._build_repository(
            collection_file_path="/users/workspace/7/7-collection.ods",
            association_count=2,
        )

        repository.reinitialize_collection(7)

        self.assertEqual([7], user_collection.deleted_users)
        self.assertEqual([7], user_file.cleared_users)
        self.assertEqual(["/users/workspace/7/7-collection.ods"], remover.deleted_paths)
        self.assertFalse(transaction.rolled_back)

    def test_reinitialize_collection_accepts_associations_without_file_path(self):
        """Verifie le nettoyage quand seules des associations existent.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le nettoyage SQL sans fichier.
        """

        repository, transaction, user_file, user_collection, remover = self._build_repository(
            collection_file_path="",
            association_count=1,
        )

        repository.reinitialize_collection(7)

        self.assertEqual([7], user_collection.deleted_users)
        self.assertEqual([7], user_file.cleared_users)
        self.assertEqual([""], remover.deleted_paths)
        self.assertFalse(transaction.rolled_back)

    def test_reinitialize_collection_rejects_missing_collection(self):
        """Verifie le refus quand aucune collection n'existe.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur fonctionnelle.
        """

        repository, transaction, user_file, user_collection, remover = self._build_repository()

        with self.assertRaises(UserCollectionReinitializationNotFoundError):
            repository.reinitialize_collection(7)

        self.assertEqual([], user_collection.deleted_users)
        self.assertEqual([], user_file.cleared_users)
        self.assertEqual([], remover.deleted_paths)
        self.assertTrue(transaction.rolled_back)

    def test_reinitialize_collection_rolls_back_on_delete_error(self):
        """Verifie le rollback si une suppression SQL echoue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le rollback transactionnel.
        """

        repository, transaction, user_file, user_collection, remover = self._build_repository(
            collection_file_path="/users/workspace/7/7-collection.ods",
            association_count=1,
            delete_error=RuntimeError("db"),
        )

        with self.assertRaises(RuntimeError):
            repository.reinitialize_collection(7)

        self.assertEqual([7], user_collection.deleted_users)
        self.assertEqual([], user_file.cleared_users)
        self.assertEqual([], remover.deleted_paths)
        self.assertTrue(transaction.rolled_back)

    def test_reinitialize_collection_rolls_back_on_file_error(self):
        """Verifie le rollback SQL si la suppression fichier echoue.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le rollback transactionnel.
        """

        repository, transaction, user_file, user_collection, remover = self._build_repository(
            collection_file_path="/users/workspace/7/7-collection.ods",
            association_count=1,
            file_error=OSError("denied"),
        )

        with self.assertRaises(OSError):
            repository.reinitialize_collection(7)

        self.assertEqual([7], user_collection.deleted_users)
        self.assertEqual([7], user_file.cleared_users)
        self.assertEqual(["/users/workspace/7/7-collection.ods"], remover.deleted_paths)
        self.assertTrue(transaction.rolled_back)

    def test_reinitialize_collection_accepts_missing_file_with_warning(self):
        """Verifie qu'un fichier absent ne bloque pas la reinitialisation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le warning et le commit SQL.
        """

        missing_path = "/tmp/cloudcollectionapp-missing-reinit-file.ods"
        logger = FakeLogger()
        repository, transaction, user_file, user_collection, remover = self._build_repository(
            collection_file_path=missing_path,
            association_count=1,
            collection_file_remover=_UserCollectionFileRemover(logger),
        )

        repository.reinitialize_collection(7)

        self.assertEqual([7], user_collection.deleted_users)
        self.assertEqual([7], user_file.cleared_users)
        self.assertTrue(logger.warnings)
        self.assertFalse(transaction.rolled_back)

    def _build_repository(
        self,
        collection_file_path="",
        association_count=0,
        delete_error=None,
        file_error=None,
        collection_file_remover=None,
    ):
        """Construit le repository d'import teste.

        Args:
            collection_file_path (str): Chemin de collection configure.
            association_count (int): Nombre d'associations configure.
            delete_error (Exception | None): Erreur SQL configuree.
            file_error (Exception | None): Erreur fichier configuree.
            collection_file_remover (object | None): Suppresseur de fichier injecte.

        Returns:
            tuple: Repository et fakes injectes.
        """

        repository = object.__new__(SqlAlchemyUserCollectionImportRepository)
        transaction = FakeTransaction(object())
        user_file = FakeUserFileRepository(collection_file_path)
        user_collection = FakeUserCollectionRepository(association_count, delete_error)
        remover = collection_file_remover or FakeCollectionFileRemover(file_error)
        repository.engine = FakeEngine(transaction)
        repository.user_file_repository = user_file
        repository.user_collection_repository = user_collection
        repository.collection_file_remover = remover
        return repository, transaction, user_file, user_collection, remover


if __name__ == "__main__":
    unittest.main()
