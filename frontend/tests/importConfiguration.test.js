/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-28
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : tests frontend de configuration d'import de collection.
 */
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildImportConfigurationDescription,
  collectionColumnFields,
  createDefaultImportConfiguration,
  wishlistSheetColumnFields,
} from "../src/hooks/collection/importConfigurationBuilder.js";

test("expose les memes informations optionnelles pour la collection et la wishlist dediee", () => {
  const configuration = createDefaultImportConfiguration();

  assert.deepEqual(wishlistSheetColumnFields(), [
    "name",
    "platform",
    "studio",
    "release_date",
    "purchase_price",
    "buy_location",
    "buy_date",
    "grade",
    "condition",
    "has_manual",
    "is_collector",
    "has_steelbook",
    "is_digital",
    "region",
    "description",
  ]);
  assert.deepEqual(
    collectionColumnFields(configuration, true).filter((field) => field !== "wishlist"),
    wishlistSheetColumnFields()
  );
});

test("serialise les colonnes optionnelles wishlist sans fusionner celles de la collection", () => {
  const configuration = createDefaultImportConfiguration();
  configuration.wishlist = {
    ...configuration.wishlist,
    mode: "sheet",
    sheetName: "Wishlist",
    layout: {
      ...configuration.wishlist.layout,
      columns: {
        ...configuration.wishlist.layout.columns,
        purchase_price: "E",
        buy_location: "F",
      },
    },
  };
  configuration.singleSheetLayout = {
    ...configuration.singleSheetLayout,
    columns: {
      ...configuration.singleSheetLayout.columns,
      grade: "G",
    },
  };

  const { description, errors } = buildImportConfigurationDescription(configuration);

  assert.deepEqual(errors, []);
  assert.equal(description.wishlist.column_information.purchase_price, "E");
  assert.equal(description.wishlist.column_information.buy_location, "F");
  assert.equal(description.wishlist.column_information.grade, undefined);
  assert.equal(description.single_sheet_conf.column_information.grade, "G");
  assert.equal(description.single_sheet_conf.column_information.purchase_price, undefined);
});
