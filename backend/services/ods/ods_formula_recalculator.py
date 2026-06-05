#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-04
# Auteurs : Codex et Binda Sébastien
# License : Apache 2.0
#
"""Recalcul des formules ODS avec LibreOffice.

Description:
    Cette classe lance LibreOffice Calc en mode headless pour recalculer et
    sauvegarder les formules apres une modification du fichier ODS.
"""

import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional


class OdsFormulaRecalculator:
    """Recalcule les formules ODS en utilisant le moteur LibreOffice Calc."""

    def __init__(self, mode: Optional[str] = None, binary_path: Optional[str] = None):
        """Initialise le service de recalcul de formules.

        Args:
            mode (str | None): `required`, `auto` ou `disabled`. Si absent, lit l'environnement.
            binary_path (str | None): Chemin explicite vers `soffice` ou `libreoffice`.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.mode = (mode or os.getenv("ODS_FORMULA_RECALCULATION", "auto")).strip().lower()
        if binary_path is None:
            self.binary_path = os.getenv("LIBREOFFICE_BIN") or self._find_binary()
        else:
            self.binary_path = binary_path

    def recalculate(self, ods_path: str) -> bool:
        """Recalcule les formules d'un ODS si LibreOffice est disponible.

        Args:
            ods_path (str): Chemin du fichier ODS a recalculer.

        Returns:
            bool: `True` si LibreOffice a recalcule le fichier, sinon `False`.
        """

        if self.mode == "disabled":
            return False
        if not self.binary_path:
            if self.mode == "required":
                raise ValueError("LibreOffice est requis pour recalculer les formules ODS.")
            return False

        self._recalculate_with_libreoffice(Path(ods_path))
        return True

    def _find_binary(self) -> Optional[str]:
        """Recherche le binaire LibreOffice disponible.

        Args:
            Aucun.

        Returns:
            str | None: Chemin du binaire trouve, sinon `None`.
        """

        return shutil.which("soffice") or shutil.which("libreoffice")

    def _recalculate_with_libreoffice(self, ods_path: Path) -> None:
        """Lance LibreOffice headless pour ouvrir, recalculer et sauvegarder.

        Args:
            ods_path (pathlib.Path): Fichier ODS cible.

        Returns:
            None: Le fichier cible est remplace par la version recalculee.
        """

        with TemporaryDirectory() as profile_dir, TemporaryDirectory() as output_dir:
            output_path = Path(output_dir) / ods_path.name
            command = [
                self.binary_path,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--norestore",
                f"-env:UserInstallation=file://{profile_dir}",
                "--convert-to",
                "ods",
                "--outdir",
                output_dir,
                str(ods_path),
            ]
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                raise ValueError(
                    "LibreOffice n'a pas pu recalculer le fichier ODS: "
                    f"{result.stderr or result.stdout}"
                )
            if not output_path.exists():
                raise ValueError("LibreOffice n'a pas produit de fichier ODS recalcule.")
            shutil.copy2(output_path, ods_path)
