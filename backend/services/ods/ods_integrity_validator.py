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
"""Validation d'integrite des fichiers ODS.

Description:
    Cette classe verifie qu'un ODS reste lisible apres modification et que les
    formules conservees dans le XML gardent une syntaxe structurelle coherente.
"""

from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

from .ods_namespaces import OdsNamespaces


class OdsIntegrityValidator:
    """Valide la structure ZIP, XML et les formules d'un fichier ODS."""

    def __init__(self):
        """Initialise le validateur ODS.

        Args:
            Aucun.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.namespaces = OdsNamespaces.values

    def validate(self, ods_path: str) -> None:
        """Valide un fichier ODS et leve une erreur en cas d'integrite invalide.

        Args:
            ods_path (str): Chemin du fichier ODS a verifier.

        Returns:
            None: La methode retourne seulement si le fichier est valide.
        """

        try:
            with ZipFile(ods_path, "r") as archive:
                self._validate_zip_members(archive)
                content = archive.read("content.xml")
        except BadZipFile as exc:
            raise ValueError("Le fichier ODS modifie n'est pas une archive valide.") from exc

        self._validate_formula_namespace_declarations(content)
        root = self._parse_content(content)
        self._validate_formulas(root)

    def _validate_formula_namespace_declarations(self, content: bytes) -> None:
        """Verifie que les prefixes de formules sont declares dans le XML.

        Args:
            content (bytes): Contenu brut de `content.xml`.

        Returns:
            None: La methode retourne si les namespaces requis existent.
        """

        if b"of:=" in content and b"xmlns:of=" not in content:
            raise ValueError("Les formules ODS utilisent le prefixe `of` sans declaration XML.")
        if b"oooc:=" in content and b"xmlns:oooc=" not in content:
            raise ValueError("Les formules ODS utilisent le prefixe `oooc` sans declaration XML.")

    def _validate_zip_members(self, archive: ZipFile) -> None:
        """Verifie les membres requis de l'archive ODS.

        Args:
            archive (zipfile.ZipFile): Archive ODS ouverte en lecture.

        Returns:
            None: La methode retourne si les membres requis existent.
        """

        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"Le fichier ODS modifie contient une entree corrompue: {bad_member}.")
        if "content.xml" not in archive.namelist():
            raise ValueError("Le fichier ODS modifie ne contient plus content.xml.")

    def _parse_content(self, content: bytes) -> ET.Element:
        """Parse le XML principal du fichier ODS.

        Args:
            content (bytes): Contenu brut de `content.xml`.

        Returns:
            xml.etree.ElementTree.Element: Racine XML parse.
        """

        try:
            return ET.fromstring(content)
        except ET.ParseError as exc:
            raise ValueError(f"Le XML ODS modifie est invalide: {exc}.") from exc

    def _validate_formulas(self, root: ET.Element) -> None:
        """Verifie la syntaxe structurelle des formules ODS conservees.

        Args:
            root (xml.etree.ElementTree.Element): Racine XML de `content.xml`.

        Returns:
            None: La methode retourne si les formules sont coherentes.
        """

        formula_attribute = f"{{{self.namespaces['table']}}}formula"
        for cell in root.findall(".//table:table-cell", self.namespaces):
            formula = cell.attrib.get(formula_attribute)
            if formula and not self._is_valid_formula(formula):
                raise ValueError(f"Formule ODS invalide apres modification: {formula}.")

    def _is_valid_formula(self, formula: str) -> bool:
        """Indique si une formule ODS est valide pour les controles disponibles.

        Args:
            formula (str): Formule ODS brute issue de `table:formula`.

        Returns:
            bool: `True` si le prefixe et la structure de formule sont valides.
        """

        if formula.startswith("of:=of:") or formula.startswith("oooc:=oooc:"):
            return False
        if formula.startswith("=of:") or formula.startswith("=oooc:"):
            return False
        return self._is_formula_balanced(formula)

    def _is_formula_balanced(self, formula: str) -> bool:
        """Controle l'equilibre des guillemets, parentheses et crochets.

        Args:
            formula (str): Formule ODS brute issue de `table:formula`.

        Returns:
            bool: `True` si la formule est structurellement equilibree.
        """

        stack = []
        in_string = False
        index = 0
        pairs = {")": "(", "]": "["}
        while index < len(formula):
            character = formula[index]
            if character == '"':
                if index + 1 < len(formula) and formula[index + 1] == '"':
                    index += 2
                    continue
                in_string = not in_string
            elif not in_string and character in "([":
                stack.append(character)
            elif not in_string and character in pairs:
                if not stack or stack.pop() != pairs[character]:
                    return False
            index += 1
        return not in_string and not stack
