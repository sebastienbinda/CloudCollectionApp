#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
import copy
import os
import shutil
from datetime import datetime
from typing import Any, Optional
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET
from .ods_archive_reader import OdsArchiveReader
from .ods_formula_recalculator import OdsFormulaRecalculator
from .ods_game_row_editor import OdsGameRowEditor
from .ods_integrity_validator import OdsIntegrityValidator
from .ods_namespaces import OdsNamespaces
from .ods_sheet_row_replacer import OdsSheetRowReplacer
from .ods_wishlist_appender import OdsWishlistAppender
from .ods_wishlist_row_editor import OdsWishlistRowEditor
from .ods_xml_reader import OdsXmlReader
class OdsWriter:
    def __init__(self, ods_path: str, archive_reader: OdsArchiveReader, xml_reader: OdsXmlReader):
        """Initialise l'ecrivain de contenu ODS.
        Args:
            ods_path (str): Chemin du fichier ODS.
            archive_reader (OdsArchiveReader): Lecteur des fichiers internes ODS.
            xml_reader (OdsXmlReader): Lecteur XML partage.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """
        OdsNamespaces.register()
        self.ods_path = ods_path
        self.archive_reader = archive_reader
        self.xml_reader = xml_reader
        self.namespaces = OdsNamespaces.values
        self.row_editor = OdsGameRowEditor(xml_reader)
        self.row_replacer = OdsSheetRowReplacer()
        self.wishlist_row_editor = OdsWishlistRowEditor(xml_reader)
        self.integrity_validator = OdsIntegrityValidator()
        self.formula_recalculator = OdsFormulaRecalculator()
    def add_game(self, platform: str, game: dict[str, Any]) -> None:
        """Ajoute un jeu dans le contenu XML de l'ODS.
        Args:
            platform (str): Onglet ODS dans lequel inserer le jeu.
            game (dict[str, Any]): Donnees du jeu deja validees et nettoyees.
        Returns:
            None: Le fichier ODS est modifie sur disque.
        """
        content = self._build_content_with_added_game(platform=platform, game=game)
        self._write_ods_content(content)
    def add_wishlist_game(self, game: dict[str, Any]) -> None:
        """Ajoute un jeu dans l'onglet `Liste de souhaits`.
        Args:
            game (dict[str, Any]): Donnees wishlist deja validees et nettoyees.
        Returns:
            None: Le fichier ODS est modifie sur disque.
        """
        appender = OdsWishlistAppender(
            self.archive_reader, self.xml_reader, self.wishlist_row_editor, self.row_replacer
        )
        self._write_ods_content(self._serialized_content(ET.fromstring(appender.build_content(game))))
    def delete_wishlist_game(self, game_name: str, console: str) -> None:
        """Supprime un jeu dans l'onglet `Liste de souhaits`.
        Args:
            game_name (str): Nom du jeu a supprimer.
            console (str): Console associee a la ligne wishlist.
        Returns:
            None: Le fichier ODS est modifie sur disque.
        """
        content = self._build_content_without_wishlist_game(game_name=game_name, console=console)
        self._write_ods_content(content)
    def update_wishlist_game(
        self,
        original_game: dict[str, Any],
        updated_game: dict[str, Any],
    ) -> None:
        """Modifie un jeu dans l'onglet `Liste de souhaits`.
        Args:
            original_game (dict[str, Any]): Donnees permettant d'identifier la ligne.
            updated_game (dict[str, Any]): Donnees wishlist validees a ecrire.
        Returns:
            None: Le fichier ODS est modifie sur disque.
        """
        content = self._build_content_with_updated_wishlist_game(original_game, updated_game)
        self._write_ods_content(content)
    def delete_game(self, platform: str, game: dict[str, Any]) -> None:
        """Vide un jeu dans une plateforme sans modifier les colonnes hors table.
        Args:
            platform (str): Onglet ODS dans lequel supprimer le jeu.
            game (dict[str, Any]): Donnees permettant d'identifier la ligne de jeu.
        Returns:
            None: Le fichier ODS est modifie sur disque.
        """
        content = self._build_content_without_game(platform=platform, game=game)
        self._write_ods_content(content)
    def update_game(
        self,
        platform: str,
        original_game: dict[str, Any],
        updated_game: dict[str, Any],
    ) -> None:
        """Modifie un jeu dans une plateforme.
        Args:
            platform (str): Onglet ODS cible.
            original_game (dict[str, Any]): Donnees d'identification.
            updated_game (dict[str, Any]): Donnees validees.
        Returns:
            None: Le fichier ODS est modifie.
        """
        content = self._build_content_with_updated_game(
            platform=platform,
            original_game=original_game,
            updated_game=updated_game,
        )
        self._write_ods_content(content)
    def _build_content_with_added_game(self, platform: str, game: dict[str, Any]) -> bytes:
        """Construit un nouveau `content.xml` avec une ligne de jeu ajoutee.
        Args:
            platform (str): Onglet ODS dans lequel inserer le jeu.
            game (dict[str, Any]): Donnees du jeu deja validees et nettoyees.
        Returns:
            bytes: Contenu XML encode en UTF-8 a reinjecter dans l'archive ODS.
        """
        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = self.xml_reader.find_sheet(root, platform)
        row_tag = f"{{{self.namespaces['table']}}}table-row"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
        direct_children = list(sheet)
        row_insert_position = next(
            (index for index, child in enumerate(direct_children) if child.tag == row_tag),
            len(direct_children),
        )
        expanded_rows = []
        for child in direct_children:
            if child.tag != row_tag:
                continue
            repeated_rows = int(child.attrib.get(repeated_rows_attribute, "1"))
            for _ in range(repeated_rows):
                expanded_row = copy.deepcopy(child)
                expanded_row.attrib.pop(repeated_rows_attribute, None)
                expanded_rows.append(expanded_row)
        stats_row_index = self._find_stats_row_index(expanded_rows)
        if stats_row_index is None:
            raise ValueError(f"Unable to find stats area in sheet '{platform}'.")
        last_game_row_index = self._find_last_game_row_index(expanded_rows, stats_row_index)
        if last_game_row_index is None:
            raise ValueError(f"Unable to find a template row in sheet '{platform}'.")
        template_row = copy.deepcopy(expanded_rows[last_game_row_index])
        target_row_index = self.row_editor.find_next_available_game_row_index(
            expanded_rows,
            last_game_row_index + 1,
        )
        if target_row_index is None:
            target_row_index = len(expanded_rows)
            expanded_rows.append(ET.Element(row_tag))
        target_row = copy.deepcopy(expanded_rows[target_row_index])
        self.row_editor.set_game_row_values(target_row, template_row, game)
        expanded_rows[target_row_index] = target_row
        self.row_replacer.replace(sheet, row_tag, row_insert_position, expanded_rows)
        return self._serialized_content(root)
    def _build_content_without_wishlist_game(self, game_name: str, console: str) -> bytes:
        """Construit un nouveau `content.xml` sans une ligne wishlist.
        Args:
            game_name (str): Nom du jeu cible.
            console (str): Console cible.
        Returns:
            bytes: Contenu XML encode en UTF-8 a reinjecter dans l'archive ODS.
        """
        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = self.xml_reader.find_sheet(root, "Liste de souhaits")
        row_tag = f"{{{self.namespaces['table']}}}table-row"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
        direct_children = list(sheet)
        row_insert_position = next(
            (index for index, child in enumerate(direct_children) if child.tag == row_tag),
            len(direct_children),
        )
        expanded_rows = self._expanded_sheet_rows(direct_children, row_tag, repeated_rows_attribute)
        target_row_index = self.wishlist_row_editor.find_wishlist_row_index(
            expanded_rows,
            {"Nom du jeu": game_name, "Console": console},
        )
        if target_row_index is None:
            raise ValueError("Le jeu est introuvable dans la liste de souhaits.")
        expanded_rows.pop(target_row_index)
        self.row_replacer.replace(sheet, row_tag, row_insert_position, expanded_rows)
        return self._serialized_content(root)
    def _build_content_with_updated_wishlist_game(
        self,
        original_game: dict[str, Any],
        updated_game: dict[str, Any],
    ) -> bytes:
        """Construit un nouveau `content.xml` avec une ligne wishlist modifiee.
        Args:
            original_game (dict[str, Any]): Donnees de recherche de la ligne cible.
            updated_game (dict[str, Any]): Donnees de remplacement validees.
        Returns:
            bytes: Contenu XML encode en UTF-8 a reinjecter dans l'archive ODS.
        """
        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = self.xml_reader.find_sheet(root, "Liste de souhaits")
        row_tag = f"{{{self.namespaces['table']}}}table-row"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
        direct_children = list(sheet)
        row_insert_position = next(
            (index for index, child in enumerate(direct_children) if child.tag == row_tag),
            len(direct_children),
        )
        expanded_rows = self._expanded_sheet_rows(direct_children, row_tag, repeated_rows_attribute)
        target_row_index = self.wishlist_row_editor.find_wishlist_row_index(expanded_rows, original_game)
        if target_row_index is None:
            raise ValueError("Le jeu est introuvable dans la liste de souhaits.")
        target_row = copy.deepcopy(expanded_rows[target_row_index])
        self.wishlist_row_editor.set_wishlist_row_values(target_row, target_row, updated_game)
        expanded_rows[target_row_index] = target_row
        self.row_replacer.replace(sheet, row_tag, row_insert_position, expanded_rows)
        return self._serialized_content(root)
    def _build_content_without_game(self, platform: str, game: dict[str, Any]) -> bytes:
        """Construit un nouveau `content.xml` avec les cellules de jeu videes.
        Args:
            platform (str): Onglet ODS dans lequel supprimer le jeu.
            game (dict[str, Any]): Donnees du jeu cible, avec au minimum `Nom du jeu`.
        Returns:
            bytes: Contenu XML encode en UTF-8 a reinjecter dans l'archive ODS.
        """
        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = self.xml_reader.find_sheet(root, platform)
        row_tag = f"{{{self.namespaces['table']}}}table-row"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
        direct_children = list(sheet)
        row_insert_position = next(
            (index for index, child in enumerate(direct_children) if child.tag == row_tag),
            len(direct_children),
        )
        expanded_rows = self._expanded_sheet_rows(direct_children, row_tag, repeated_rows_attribute)
        target_row_index = self.row_editor.find_game_row_index(expanded_rows, game)
        if target_row_index is None:
            raise ValueError("Le jeu est introuvable dans la plateforme.")
        target_row = copy.deepcopy(expanded_rows[target_row_index])
        self.row_editor.clear_game_row_values(target_row)
        expanded_rows[target_row_index] = target_row
        self.row_replacer.replace(sheet, row_tag, row_insert_position, expanded_rows)
        return self._serialized_content(root)
    def _build_content_with_updated_game(
        self,
        platform: str,
        original_game: dict[str, Any],
        updated_game: dict[str, Any],
    ) -> bytes:
        """Construit un `content.xml` avec une ligne modifiee.
        Args:
            platform (str): Onglet ODS cible.
            original_game (dict[str, Any]): Donnees de recherche.
            updated_game (dict[str, Any]): Donnees de remplacement.
        Returns:
            bytes: XML encode en UTF-8.
        """
        root = ET.fromstring(self.archive_reader.read_file("content.xml"))
        sheet = self.xml_reader.find_sheet(root, platform)
        row_tag = f"{{{self.namespaces['table']}}}table-row"
        repeated_rows_attribute = f"{{{self.namespaces['table']}}}number-rows-repeated"
        direct_children = list(sheet)
        row_insert_position = next(
            (index for index, child in enumerate(direct_children) if child.tag == row_tag),
            len(direct_children),
        )
        expanded_rows = self._expanded_sheet_rows(direct_children, row_tag, repeated_rows_attribute)
        target_row_index = self.row_editor.find_game_row_index(expanded_rows, original_game)
        if target_row_index is None:
            raise ValueError("Le jeu est introuvable dans la plateforme.")
        target_row = copy.deepcopy(expanded_rows[target_row_index])
        self.row_editor.set_game_row_values(target_row, target_row, updated_game)
        expanded_rows[target_row_index] = target_row
        self.row_replacer.replace(sheet, row_tag, row_insert_position, expanded_rows)
        return self._serialized_content(root)
    def _expanded_sheet_rows(
        self,
        direct_children: list[ET.Element],
        row_tag: str,
        repeated_rows_attribute: str,
    ) -> list[ET.Element]:
        """Expanse les lignes XML repetees d'une feuille ODS.
        Args:
            direct_children (list[xml.etree.ElementTree.Element]): Enfants directs de la feuille.
            row_tag (str): Balise XML des lignes.
            repeated_rows_attribute (str): Attribut ODS de repetition de lignes.
        Returns:
            list[xml.etree.ElementTree.Element]: Lignes clonees sans attribut de repetition.
        """
        expanded_rows = []
        for child in direct_children:
            if child.tag != row_tag:
                continue
            repeated_rows = int(child.attrib.get(repeated_rows_attribute, "1"))
            for _ in range(repeated_rows):
                expanded_row = copy.deepcopy(child)
                expanded_row.attrib.pop(repeated_rows_attribute, None)
                expanded_rows.append(expanded_row)
        return expanded_rows
    def _write_ods_content(self, content: bytes) -> None:
        """Ecrit le nouveau `content.xml` dans le fichier ODS.
        Args:
            content (bytes): XML complet de `content.xml` apres modification.
        Returns:
            None: La methode modifie le fichier ODS sur disque.
        """
        backup_path = self._build_backup_path()
        shutil.copy2(self.ods_path, backup_path)
        tmp_path = self._build_tmp_path()
        with ZipFile(self.ods_path, "r") as source_archive:
            with ZipFile(tmp_path, "w", compression=ZIP_DEFLATED) as target_archive:
                for item in source_archive.infolist():
                    if item.filename == "content.xml":
                        target_archive.writestr(item, content)
                    else:
                        target_archive.writestr(item, source_archive.read(item.filename))
        self._publish_tmp_ods(tmp_path)
        try:
            self.integrity_validator.validate(self.ods_path)
            self.formula_recalculator.recalculate(self.ods_path)
            self.integrity_validator.validate(self.ods_path)
        except Exception as exc:
            shutil.copy2(backup_path, self.ods_path)
            raise ValueError(
                "Modification ODS annulee: le fichier modifie est invalide. "
                f"Backup restaure depuis {backup_path}. Detail: {exc}"
            ) from exc
    def _build_backup_path(self) -> str:
        """Construit le chemin de sauvegarde du fichier ODS courant.
        Args:
            Aucun.
        Returns:
            str: Chemin complet du fichier de sauvegarde.
        """
        backup_dir = self._get_work_directory("JEUXVIDEO_ODS_BACKUP_DIR")
        backup_name = f"{os.path.basename(self.ods_path)}.backup-{self._timestamp()}"
        return os.path.join(backup_dir, backup_name)
    def _build_tmp_path(self) -> str:
        """Construit le chemin temporaire utilise pour reecrire l'ODS.
        Args:
            Aucun.
        Returns:
            str: Chemin complet du fichier temporaire.
        """
        tmp_dir = self._get_work_directory("JEUXVIDEO_ODS_TMP_DIR")
        tmp_name = f"{os.path.basename(self.ods_path)}.{self._timestamp()}.tmp"
        return os.path.join(tmp_dir, tmp_name)
    def _get_work_directory(self, env_name: str) -> str:
        """Retourne un repertoire de travail configure ou voisin de l'ODS.
        Args:
            env_name (str): Nom de la variable d'environnement a lire.
        Returns:
            str: Repertoire existant pret a recevoir des fichiers.
        """
        directory = os.getenv(env_name) or os.path.dirname(os.path.abspath(self.ods_path))
        os.makedirs(directory, exist_ok=True)
        return directory
    def _publish_tmp_ods(self, tmp_path: str) -> None:
        """Publie le fichier temporaire vers le chemin ODS final.
        Args:
            tmp_path (str): Chemin du fichier temporaire ODS.
        Returns:
            None: Le fichier ODS final est remplace ou recopie.
        """
        same_directory = os.path.dirname(os.path.abspath(tmp_path)) == os.path.dirname(
            os.path.abspath(self.ods_path)
        )
        if same_directory:
            os.replace(tmp_path, self.ods_path)
            return
        shutil.copy2(tmp_path, self.ods_path)
        os.remove(tmp_path)
    def _timestamp(self) -> str:
        """Retourne un horodatage precis pour nommer les fichiers de travail.
        Args:
            Aucun.
        Returns:
            str: Horodatage au format `YYYYMMDDHHMMSSffffff`.
        """
        return datetime.now().strftime("%Y%m%d%H%M%S%f")
    def _serialized_content(self, root: ET.Element) -> bytes:
        """Serialise le XML ODS en normalisant les prefixes de formules.
        Args:
            root (xml.etree.ElementTree.Element): Racine XML ODS a serialiser.
        Returns:
            bytes: XML encode en UTF-8 pret a ecrire dans l'archive ODS.
        """
        self._normalize_formula_attributes(root)
        self._invalidate_formula_cached_values(root)
        content = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        return self._ensure_formula_namespace_declarations(content)
    def _normalize_formula_attributes(self, root: ET.Element) -> None:
        """Retire les prefixes de formule ODS dupliques avant ecriture.
        Args:
            root (xml.etree.ElementTree.Element): Racine XML ODS a corriger.
        Returns:
            None: Les attributs de formule sont modifies en place si necessaire.
        """
        formula_attribute = f"{{{self.namespaces['table']}}}formula"
        for cell in root.findall(".//table:table-cell", self.namespaces):
            formula = cell.attrib.get(formula_attribute)
            if formula:
                cell.attrib[formula_attribute] = self._normalized_formula(formula)
    def _normalized_formula(self, formula: str) -> str:
        """Normalise le prefixe d'une formule ODS.
        Args:
            formula (str): Formule ODS brute.
        Returns:
            str: Formule avec un seul prefixe `of:=` ou `oooc:=`.
        """
        for prefix in ["of:=", "oooc:="]:
            while formula.startswith(f"{prefix}{prefix}"):
                formula = formula[len(prefix):]
        if formula.startswith("=of:"):
            return f"of:={formula[len('=of:'):]}"
        if formula.startswith("=oooc:"):
            return f"oooc:={formula[len('=oooc:'):]}"
        return formula
    def _invalidate_formula_cached_values(self, root: ET.Element) -> None:
        """Force le recalcul des formules en supprimant leurs resultats en cache.
        Args:
            root (xml.etree.ElementTree.Element): Racine XML ODS a corriger.
        Returns:
            None: Les cellules de formule sont marquees pour recalcul.
        """
        formula_attribute = f"{{{self.namespaces['table']}}}formula"
        recalculate_attribute = f"{{{self.namespaces['table']}}}recalculate"
        cached_attributes = [
            f"{{{self.namespaces['office']}}}value",
            f"{{{self.namespaces['office']}}}date-value",
            f"{{{self.namespaces['office']}}}time-value",
            f"{{{self.namespaces['office']}}}boolean-value",
            f"{{{self.namespaces['office']}}}string-value",
            f"{{{self.namespaces['calcext']}}}value-type",
        ]
        for cell in root.findall(".//table:table-cell", self.namespaces):
            if formula_attribute not in cell.attrib:
                continue
            cell.attrib[recalculate_attribute] = "true"
            for attribute in cached_attributes:
                cell.attrib.pop(attribute, None)
            for child in list(cell):
                cell.remove(child)
    def _ensure_formula_namespace_declarations(self, content: bytes) -> bytes:
        """Ajoute les declarations de namespaces utilisees dans les formules.
        Args:
            content (bytes): XML ODS serialise.
        Returns:
            bytes: XML avec les namespaces de formule requis.
        """
        declarations = []
        if b"of:=" in content and b"xmlns:of=" not in content:
            declarations.append(
                b'xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"'
            )
        if b"oooc:=" in content and b"xmlns:oooc=" not in content:
            declarations.append(b'xmlns:oooc="http://openoffice.org/2004/calc"')
        if not declarations:
            return content
        marker = b":document-content"
        marker_index = content.find(marker)
        if marker_index < 0:
            return content
        tag_start_index = content.rfind(b"<", 0, marker_index)
        if tag_start_index < 0:
            return content
        insert_index = marker_index + len(marker)
        return content[:insert_index] + b" " + b" ".join(declarations) + content[insert_index:]
    def _find_stats_row_index(self, rows: list[ET.Element]) -> Optional[int]:
        """Trouve l'index de la ligne qui marque la zone de statistiques.
        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.
        Returns:
            Optional[int]: Index de la ligne contenant `Nombre de Jeux`, sinon `None`.
        """
        for index, row in enumerate(rows):
            if "Nombre de Jeux" in self.xml_reader.row_text_values(row):
                return index
        return None
    def _find_last_game_row_index(self, rows: list[ET.Element], stats_row_index: int) -> Optional[int]:
        """Trouve la derniere ligne de jeu avant les statistiques.
        Args:
            rows (list[xml.etree.ElementTree.Element]): Lignes XML deja expansees.
            stats_row_index (int): Index de debut de la zone de statistiques.
        Returns:
            Optional[int]: Index de la derniere ligne contenant un nom de jeu, sinon `None`.
        """
        last_game_row_index = None
        for index in range(6, stats_row_index):
            cells = self.xml_reader.expanded_cells(rows[index])
            game_name = self.xml_reader.cell_text_value(cells[5]) if len(cells) > 5 else None
            if game_name:
                last_game_row_index = index
        return last_game_row_index
