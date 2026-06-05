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
"""Tests de l'ecriture ODS.
Description:
    Ce module valide que l'ecrivain ODS limite les modifications aux cellules
    necessaires du tableau des jeux.
"""
import unittest
import xml.etree.ElementTree as ET
import os
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile
from services.ods import OdsNamespaces, OdsWriter
from services.ods.ods_xml_reader import OdsXmlReader
class FakeArchiveReader:
    """Lecteur d'archive factice pour fournir un `content.xml` en memoire."""
    def __init__(self, content: bytes):
        """Initialise le lecteur factice.
        Args:
            content (bytes): Contenu XML retourne par le lecteur.
        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """
        self.content = content
    def read_file(self, path: str) -> bytes:
        """Retourne le contenu XML du fichier demande.
        Args:
            path (str): Chemin interne demande dans l'archive ODS.
        Returns:
            bytes: Contenu XML factice.
        """
        return self.content
class FailingFormulaRecalculator:
    """Recalculateur factice qui simule un echec LibreOffice."""
    def recalculate(self, ods_path: str) -> bool:
        """Declenche une erreur de recalcul.
        Args:
            ods_path (str): Chemin ODS ignore.
        Returns:
            bool: Ne retourne jamais.
        """
        raise ValueError("Erreur LibreOffice simulee.")
class SuccessfulFormulaRecalculator:
    """Recalculateur factice qui simule un recalcul reussi."""
    def recalculate(self, ods_path: str) -> bool:
        """Retourne un succes sans modifier le fichier.
        Args:
            ods_path (str): Chemin ODS recalcule.
        Returns:
            bool: Resultat de recalcul simule.
        """
        return True
class OdsWriterTest(unittest.TestCase):
    """Tests unitaires du comportement d'ajout de jeux dans un ODS."""
    def setUp(self):
        """Prepare les namespaces ODS pour les tests XML.
        Args:
            Aucun.
        Returns:
            None: Les namespaces sont enregistres.
        """
        OdsNamespaces.register()
        self.namespaces = OdsNamespaces.values
    def test_add_game_preserves_left_columns_on_target_row(self):
        """Verifie que l'ajout d'un jeu ne modifie pas les colonnes A a E.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la preservation des cellules hors table.
        """
        content = self._build_sheet_content()
        xml_reader = OdsXmlReader.__new__(OdsXmlReader)
        xml_reader.namespaces = self.namespaces
        writer = OdsWriter(
            ods_path="/tmp/fake.ods",
            archive_reader=FakeArchiveReader(content),
            xml_reader=xml_reader,
        )
        updated_content = writer._build_content_with_added_game(
            platform="Switch",
            game={
                "Nom du jeu": "Metroid Prime",
                "Studio": "Retro Studios",
                "Date de sortie": "2002-11-18",
                "Date d'achat": "",
                "Lieu d'achat": "Boutique",
                "Note": "Excellent",
                "Prix d'achat": "39.99",
                "Version": "PAL",
            },
        )
        rows = self._read_rows(updated_content)
        target_row_values = rows[7]
        self.assertEqual("Note gauche", target_row_values[0])
        self.assertEqual("Infos libres", target_row_values[4])
        self.assertEqual("Metroid Prime", target_row_values[5])
        self.assertEqual("Retro Studios", target_row_values[6])
        self.assertEqual("PAL", target_row_values[12])
    def test_add_game_uses_stats_row_when_game_columns_are_empty(self):
        """Verifie l'ajout sur une ligne contenant des donnees a gauche.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident que seules les colonnes de jeu changent.
        """
        content = self._build_sheet_content(with_free_row=False)
        xml_reader = OdsXmlReader.__new__(OdsXmlReader)
        xml_reader.namespaces = self.namespaces
        writer = OdsWriter(
            ods_path="/tmp/fake.ods",
            archive_reader=FakeArchiveReader(content),
            xml_reader=xml_reader,
        )
        updated_content = writer._build_content_with_added_game(
            platform="Switch",
            game={
                "Nom du jeu": "Metroid Prime",
                "Studio": "Retro Studios",
                "Date de sortie": "",
                "Date d'achat": "",
                "Lieu d'achat": "",
                "Note": "",
                "Prix d'achat": "",
                "Version": "",
            },
        )
        rows = self._read_rows(updated_content)
        target_row_values = rows[7]
        self.assertEqual("Nombre de Jeux", target_row_values[0])
        self.assertEqual("Metroid Prime", target_row_values[5])
        self.assertEqual("Retro Studios", target_row_values[6])
    def test_delete_game_clears_game_columns_and_preserves_left_columns(self):
        """Verifie que la suppression vide F a M sans modifier A a E.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident la preservation des colonnes hors table.
        """
        content = self._build_sheet_content()
        xml_reader = OdsXmlReader.__new__(OdsXmlReader)
        xml_reader.namespaces = self.namespaces
        writer = OdsWriter(
            ods_path="/tmp/fake.ods",
            archive_reader=FakeArchiveReader(content),
            xml_reader=xml_reader,
        )
        updated_content = writer._build_content_without_game(
            platform="Switch",
            game={
                "Nom du jeu": "Zelda",
                "Studio": "Nintendo",
                "Date de sortie": "",
                "Date d'achat": "",
                "Lieu d'achat": "",
                "Note": "",
                "Prix d'achat": "",
                "Version": "PAL",
            },
        )
        rows = self._read_rows(updated_content)
        target_row_values = rows[6]
        self.assertEqual("Info gauche", target_row_values[0])
        self.assertTrue(all(value is None for value in target_row_values[5:13]))
    def test_delete_game_falls_back_to_unique_name_when_values_differ(self):
        """Verifie la suppression par nom unique si les valeurs formatees different.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident le fallback d'identification.
        """
        content = self._build_sheet_content()
        xml_reader = OdsXmlReader.__new__(OdsXmlReader)
        xml_reader.namespaces = self.namespaces
        writer = OdsWriter(
            ods_path="/tmp/fake.ods",
            archive_reader=FakeArchiveReader(content),
            xml_reader=xml_reader,
        )
        updated_content = writer._build_content_without_game(
            platform="Switch",
            game={
                "Nom du jeu": "Zelda",
                "Studio": "Valeur affichee differente",
                "Date de sortie": "",
                "Date d'achat": "",
                "Lieu d'achat": "",
                "Note": "",
                "Prix d'achat": "",
                "Version": "",
            },
        )
        rows = self._read_rows(updated_content)
        self.assertEqual("Info gauche", rows[6][0])
        self.assertTrue(all(value is None for value in rows[6][5:13]))
    def test_update_game_replaces_game_columns_and_preserves_left_columns(self):
        """Verifie que la modification remplace F a M sans modifier A a E.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident les cellules modifiees.
        """
        writer = OdsWriter(
            ods_path="/tmp/fake.ods",
            archive_reader=FakeArchiveReader(self._build_sheet_content()),
            xml_reader=self._xml_reader(),
        )
        updated_content = writer._build_content_with_updated_game(
            platform="Switch",
            original_game={"Nom du jeu": "Zelda", "Studio": "Nintendo"},
            updated_game={
                "Nom du jeu": "Zelda Deluxe",
                "Studio": "Nintendo",
                "Date de sortie": "2024-01-01",
                "Date d'achat": "2026-05-06",
                "Lieu d'achat": "Eshop",
                "Note": "9/10",
                "Prix d'achat": "0",
                "Version": "PAL FR",
            },
        )
        rows = self._read_rows(updated_content)
        self.assertEqual("Info gauche", rows[6][0])
        self.assertEqual("Zelda Deluxe", rows[6][5])
        self.assertEqual("2026-05-06", rows[6][8])
        self.assertEqual("0", rows[6][11])
    def test_update_wishlist_game_replaces_wishlist_columns(self):
        """Verifie la modification d'une ligne de liste de souhaits.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident les cellules wishlist modifiees.
        """
        writer = OdsWriter(
            ods_path="/tmp/fake.ods",
            archive_reader=FakeArchiveReader(self._build_wishlist_content()),
            xml_reader=self._xml_reader(),
        )
        updated_content = writer._build_content_with_updated_wishlist_game(
            original_game={"Nom du jeu": "Chrono Trigger", "Console": "Switch 2"},
            updated_game={
                "Nom du jeu": "Chrono Trigger HD",
                "Console": "Switch 2",
                "Studio": "Square",
                "Date de sortie": "2026-06-01",
                "Date d'achat": "",
                "Lieu d'achat": "",
                "Prix d'achat": "59.99",
            },
        )
        rows = self._read_rows(updated_content, "Liste de souhaits")
        self.assertEqual("Note gauche", rows[6][0])
        self.assertEqual("Chrono Trigger HD", rows[6][5])
        self.assertEqual("Switch 2", rows[6][6])
        self.assertEqual("Square", rows[6][7])
    def test_write_ods_content_restores_backup_when_validation_fails(self):
        """Verifie la restauration du backup si le fichier modifie est invalide.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident que le fichier original est restaure.
        """
        with TemporaryDirectory() as directory:
            ods_path = f"{directory}/collection.ods"
            original_content = self._build_sheet_content()
            self._write_ods_file(ods_path, original_content)
            writer = OdsWriter(
                ods_path=ods_path,
                archive_reader=FakeArchiveReader(original_content),
                xml_reader=self._xml_reader(),
            )
            with self.assertRaises(ValueError):
                writer._write_ods_content(self._build_formula_content('of:=SUM([.A1:.A2]'))
            with ZipFile(ods_path, "r") as archive:
                restored_content = archive.read("content.xml")
            self.assertEqual(original_content, restored_content)
    def test_write_ods_content_restores_backup_when_recalculation_fails(self):
        """Verifie la restauration du backup si LibreOffice echoue.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident que le fichier original est restaure.
        """
        with TemporaryDirectory() as directory:
            ods_path = f"{directory}/collection.ods"
            original_content = self._build_sheet_content()
            self._write_ods_file(ods_path, original_content)
            writer = OdsWriter(
                ods_path=ods_path,
                archive_reader=FakeArchiveReader(original_content),
                xml_reader=self._xml_reader(),
            )
            writer.formula_recalculator = FailingFormulaRecalculator()
            with self.assertRaises(ValueError):
                writer._write_ods_content(self._build_sheet_content())
            with ZipFile(ods_path, "r") as archive:
                restored_content = archive.read("content.xml")
            self.assertEqual(original_content, restored_content)
    def test_write_ods_content_uses_configured_tmp_and_backup_directories(self):
        """Verifie les repertoires separes pour les temporaires et backups.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident les chemins de travail configures.
        """
        with TemporaryDirectory() as directory:
            ods_path = f"{directory}/collection.ods"
            tmp_dir = f"{directory}/tmp"
            backup_dir = f"{directory}/backup"
            original_content = self._build_sheet_content()
            updated_content = self._build_wishlist_content()
            self._write_ods_file(ods_path, original_content)
            writer = OdsWriter(
                ods_path=ods_path,
                archive_reader=FakeArchiveReader(original_content),
                xml_reader=self._xml_reader(),
            )
            writer.formula_recalculator = SuccessfulFormulaRecalculator()
            with patch.dict(
                os.environ,
                {
                    "JEUXVIDEO_ODS_TMP_DIR": tmp_dir,
                    "JEUXVIDEO_ODS_BACKUP_DIR": backup_dir,
                },
            ):
                writer._write_ods_content(updated_content)
            with ZipFile(ods_path, "r") as archive:
                written_content = archive.read("content.xml")
            self.assertEqual(updated_content, written_content)
            self.assertEqual([], os.listdir(tmp_dir))
            backups = os.listdir(backup_dir)
            self.assertEqual(1, len(backups))
            self.assertTrue(backups[0].startswith("collection.ods.backup-"))
    def test_add_wishlist_game_writes_next_available_row(self):
        """Verifie l'ajout d'un jeu dans la liste de souhaits.
        Args:
            Aucun.
        Returns:
            None: Les assertions valident l'ecriture de la ligne wishlist.
        """
        with TemporaryDirectory() as directory:
            ods_path = f"{directory}/collection.ods"
            original_content = self._build_wishlist_content()
            self._write_ods_file(ods_path, original_content)
            writer = OdsWriter(
                ods_path=ods_path,
                archive_reader=FakeArchiveReader(original_content),
                xml_reader=self._xml_reader(),
            )
            writer.formula_recalculator = SuccessfulFormulaRecalculator()
            writer.add_wishlist_game(
                {
                    "Nom du jeu": "Chrono Trigger HD",
                    "Console": "Switch 2",
                    "Studio": "Square",
                    "Date de sortie": "",
                    "Date d'achat": "",
                    "Lieu d'achat": "",
                    "Prix d'achat": "59.99",
                }
            )
            with ZipFile(ods_path, "r") as archive:
                updated_content = archive.read("content.xml")
            rows = self._read_rows(updated_content, "Liste de souhaits")
            self.assertEqual("Chrono Trigger HD", rows[7][5])
            self.assertEqual("Switch 2", rows[7][6])
    def _build_sheet_content(self, with_free_row: bool = True) -> bytes:
        """Construit un `content.xml` minimal pour tester l'ecriture.
        Args:
            with_free_row (bool): Indique si une ligne libre existe avant les statistiques.
        Returns:
            bytes: XML ODS minimal encode en UTF-8.
        """
        office = self.namespaces["office"]
        table = self.namespaces["table"]
        root = ET.Element(f"{{{office}}}document-content")
        body = ET.SubElement(root, f"{{{office}}}body")
        spreadsheet = ET.SubElement(body, f"{{{office}}}spreadsheet")
        sheet = ET.SubElement(spreadsheet, f"{{{table}}}table", {f"{{{table}}}name": "Switch"})
        for _ in range(6):
            sheet.append(self._row([""] * 13))
        sheet.append(self._row(["Info gauche"] + [""] * 4 + ["Zelda", "Nintendo", "", "", "", "", "", "PAL"]))
        if with_free_row:
            sheet.append(self._row(["Note gauche", "", "", "", "Infos libres"] + [""] * 8))
        sheet.append(self._row(["Nombre de Jeux"] + [""] * 12))
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    def _build_wishlist_content(self) -> bytes:
        """Construit un `content.xml` minimal pour la wishlist.
        Args:
            Aucun.
        Returns:
            bytes: XML ODS minimal encode en UTF-8.
        """
        office = self.namespaces["office"]
        table = self.namespaces["table"]
        root = ET.Element(f"{{{office}}}document-content")
        body = ET.SubElement(root, f"{{{office}}}body")
        spreadsheet = ET.SubElement(body, f"{{{office}}}spreadsheet")
        sheet = ET.SubElement(spreadsheet, f"{{{table}}}table", {f"{{{table}}}name": "Liste de souhaits"})
        for _ in range(6):
            sheet.append(self._row([""] * 12))
        sheet.append(self._row(["Note gauche"] + [""] * 4 + ["Chrono Trigger", "Switch 2", "Square", "", "", "", "60"]))
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    def _build_formula_content(self, formula: str) -> bytes:
        """Construit un `content.xml` minimal contenant une formule.
        Args:
            formula (str): Formule ODS a placer dans une cellule.
        Returns:
            bytes: XML ODS minimal encode en UTF-8.
        """
        office = self.namespaces["office"]
        table = self.namespaces["table"]
        root = ET.Element(f"{{{office}}}document-content")
        body = ET.SubElement(root, f"{{{office}}}body")
        spreadsheet = ET.SubElement(body, f"{{{office}}}spreadsheet")
        sheet = ET.SubElement(spreadsheet, f"{{{table}}}table", {f"{{{table}}}name": "Switch"})
        row = ET.SubElement(sheet, f"{{{table}}}table-row")
        ET.SubElement(row, f"{{{table}}}table-cell", {f"{{{table}}}formula": formula})
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    def _row(self, values: list[str]) -> ET.Element:
        """Construit une ligne ODS avec les valeurs donnees.
        Args:
            values (list[str]): Valeurs textuelles a placer dans les cellules.
        Returns:
            xml.etree.ElementTree.Element: Ligne XML ODS.
        """
        table = self.namespaces["table"]
        row = ET.Element(f"{{{table}}}table-row")
        for value in values:
            row.append(self._cell(value))
        return row
    def _cell(self, value: str) -> ET.Element:
        """Construit une cellule ODS textuelle.
        Args:
            value (str): Texte visible de la cellule.
        Returns:
            xml.etree.ElementTree.Element: Cellule XML ODS.
        """
        office = self.namespaces["office"]
        table = self.namespaces["table"]
        text = self.namespaces["text"]
        cell = ET.Element(f"{{{table}}}table-cell")
        if value:
            cell.attrib[f"{{{office}}}value-type"] = "string"
            paragraph = ET.SubElement(cell, f"{{{text}}}p")
            paragraph.text = value
        return cell
    def _read_rows(self, content: bytes, sheet_name: str = "Switch") -> list[list[str]]:
        """Lit les valeurs textuelles des lignes d'un XML ODS.
        Args:
            content (bytes): XML ODS a parser.
            sheet_name (str): Nom de la feuille ODS a lire.
        Returns:
            list[list[str]]: Valeurs textuelles par ligne et colonne.
        """
        xml_reader = self._xml_reader()
        root = ET.fromstring(content)
        sheet = xml_reader.find_sheet(root, sheet_name)
        return [
            [xml_reader.cell_text_value(cell) for cell in xml_reader.expanded_cells(row)]
            for row in sheet.findall("table:table-row", self.namespaces)
        ]
    def _xml_reader(self) -> OdsXmlReader:
        """Construit un lecteur XML minimal pour les tests.
        Args:
            Aucun.
        Returns:
            OdsXmlReader: Lecteur XML initialise avec les namespaces.
        """
        xml_reader = OdsXmlReader.__new__(OdsXmlReader)
        xml_reader.namespaces = self.namespaces
        return xml_reader
    def _write_ods_file(self, path: str, content: bytes) -> None:
        """Ecrit un fichier ODS minimal pour les tests.
        Args:
            path (str): Chemin du fichier ODS a creer.
            content (bytes): Contenu de `content.xml`.
        Returns:
            None: Le fichier ZIP ODS est cree.
        """
        with ZipFile(path, "w") as archive:
            archive.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
            archive.writestr("content.xml", content)
if __name__ == "__main__":
    unittest.main()
