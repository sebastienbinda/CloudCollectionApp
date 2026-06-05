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
"""Tests d'integrite des formules ODS.

Description:
    Ce module verifie que les formules restent valides et recalculees apres
    serialisation du fichier ODS.
"""

import unittest
import xml.etree.ElementTree as ET
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from services.ods import OdsNamespaces, OdsWriter
from services.ods.ods_integrity_validator import OdsIntegrityValidator
from services.ods.ods_xml_reader import OdsXmlReader


class FakeArchiveReader:
    """Lecteur d'archive factice pour initialiser `OdsWriter`."""

    def __init__(self, content: bytes):
        """Initialise le lecteur factice.

        Args:
            content (bytes): Contenu XML retourne par le lecteur.

        Returns:
            None: Le constructeur ne retourne aucune valeur.
        """

        self.content = content


class OdsFormulaIntegrityTest(unittest.TestCase):
    """Tests unitaires des protections de formules ODS."""

    def setUp(self):
        """Prepare les namespaces ODS pour les tests XML.

        Args:
            Aucun.

        Returns:
            None: Les namespaces sont enregistres.
        """

        OdsNamespaces.register()
        self.namespaces = OdsNamespaces.values

    def test_integrity_validator_rejects_unbalanced_formula(self):
        """Verifie que les formules mal formees sont rejetees.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de validation.
        """

        with TemporaryDirectory() as directory:
            ods_path = f"{directory}/invalid-formula.ods"
            self._write_ods_file(ods_path, self._build_formula_content('of:=SUM([.A1:.A2]'))

            with self.assertRaises(ValueError):
                OdsIntegrityValidator().validate(ods_path)

    def test_integrity_validator_rejects_duplicated_formula_prefix(self):
        """Verifie que les prefixes de formule dupliques sont rejetes.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de validation.
        """

        with TemporaryDirectory() as directory:
            ods_path = f"{directory}/duplicated-prefix.ods"
            self._write_ods_file(ods_path, self._build_formula_content("of:=of:=SUM([.A1:.A2])"))

            with self.assertRaises(ValueError):
                OdsIntegrityValidator().validate(ods_path)

    def test_writer_normalizes_duplicated_formula_prefix(self):
        """Verifie que le writer corrige les prefixes de formule dupliques.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la formule serialisee.
        """

        writer = self._writer()
        root = ET.fromstring(self._build_formula_content("of:=of:=SUM([.A1:.A2])"))
        content = writer._serialized_content(root)

        self.assertIn(b"of:=SUM([.A1:.A2])", content)
        self.assertNotIn(b"of:=of:=", content)

    def test_writer_preserves_formula_namespace_declaration(self):
        """Verifie que le namespace `of` reste declare apres serialisation.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident la declaration de namespace.
        """

        writer = self._writer()
        root = ET.fromstring(self._build_formula_content("of:=SUM([.A1:.A2])"))
        content = writer._serialized_content(root)

        self.assertIn(b"xmlns:of=", content)

    def test_writer_marks_formula_cells_for_recalculation(self):
        """Verifie que les resultats calcules en cache sont invalides.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident le recalcul force des formules.
        """

        writer = self._writer()
        root = ET.fromstring(self._build_formula_content("of:=SUM([.A1:.A2])"))
        cell = root.find(".//table:table-cell", self.namespaces)
        cell.attrib[f"{{{self.namespaces['office']}}}value-type"] = "float"
        cell.attrib[f"{{{self.namespaces['office']}}}value"] = "65"
        cell.attrib[f"{{{self.namespaces['calcext']}}}value-type"] = "float"
        ET.SubElement(cell, f"{{{self.namespaces['text']}}}p").text = "65"

        content = writer._serialized_content(root)

        self.assertIn(b'table:recalculate="true"', content)
        self.assertNotIn(b'office:value="65"', content)
        self.assertNotIn(b">65<", content)

    def test_integrity_validator_rejects_missing_formula_namespace(self):
        """Verifie qu'une formule avec prefixe non declare est rejetee.

        Args:
            Aucun.

        Returns:
            None: Les assertions valident l'erreur de namespace.
        """

        with TemporaryDirectory() as directory:
            ods_path = f"{directory}/missing-namespace.ods"
            content = self._build_formula_content("of:=SUM([.A1:.A2])")
            content = content.replace(
                b' xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"',
                b"",
            )
            self._write_ods_file(ods_path, content)

            with self.assertRaises(ValueError):
                OdsIntegrityValidator().validate(ods_path)

    def _writer(self) -> OdsWriter:
        """Construit un writer ODS minimal pour les tests.

        Args:
            Aucun.

        Returns:
            OdsWriter: Writer initialise avec un XML minimal.
        """

        return OdsWriter(
            ods_path="/tmp/fake.ods",
            archive_reader=FakeArchiveReader(self._build_formula_content("of:=1")),
            xml_reader=self._xml_reader(),
        )

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
