/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-19
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : section admin de moderation des images de plateformes.
 */
import ProgressBar from "./ProgressBar";
import TableComponent from "./TableComponent";

const COLUMNS = [
  "platform_name",
  "status",
  "type",
  "thumbnail",
  "user_id",
  "user_email",
  "creation_date",
];
const COLUMN_LABELS = {
  platform_name: "Plateforme",
  status: "Statut",
  type: "Type",
  thumbnail: "Miniature",
  user_id: "User ID",
  user_email: "Utilisateur",
  creation_date: "Creation",
};
const STATUS_LABELS = {
  WAITING_VALIDATION: "En attente",
  ACCEPTED: "Acceptee",
};
const SORTABLE_COLUMNS = ["platform_name", "status", "type", "creation_date"];

/**
 * Affiche les filtres, le tableau et les actions de moderation d'images.
 *
 * @param {Object} props - Etat du hook de moderation des images.
 * @returns {import("react").JSX.Element|null} Section admin ou absence.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function PlatformImageModerationSection({ moderation }) {
  if (!moderation?.enabled) {
    return null;
  }

  return (
    <section className="platformImageModerationSection" aria-label="Moderation des images">
      <div className="platformImageModerationHeader">
        <div>
          <span>Images</span>
          <h2>Moderation des images de plateformes</h2>
        </div>
        <button type="button" onClick={moderation.refresh} disabled={moderation.isLoading}>
          Actualiser
        </button>
      </div>

      <form className="platformImageModerationFilters">
        <label>
          <span>Statut</span>
          <select
            value={moderation.statusFilter}
            onChange={(event) => moderation.setStatusFilter(event.target.value)}
            disabled={moderation.isLoading}
          >
            <option value="">Tous les statuts</option>
            <option value="WAITING_VALIDATION">En attente</option>
            <option value="ACCEPTED">Acceptees</option>
          </select>
        </label>
        <label>
          <span>Plateforme</span>
          <select
            value={moderation.platformFilter}
            onChange={(event) => moderation.setPlatformFilter(event.target.value)}
            disabled={moderation.isLoading}
          >
            <option value="">Toutes les plateformes</option>
            {moderation.platformOptions.map((platformName) => (
              <option key={platformName} value={platformName}>
                {platformName}
              </option>
            ))}
          </select>
        </label>
      </form>

      {moderation.isLoading ? <ProgressBar label="Chargement des images a moderer" /> : null}
      {moderation.error ? <p className="error">{moderation.error}</p> : null}
      {moderation.message ? <p className="success">{moderation.message}</p> : null}
      {!moderation.isLoading && moderation.images.length === 0 ? (
        <p>Aucune image a moderer.</p>
      ) : null}

      {moderation.images.length > 0 ? (
        <TableComponent
          rows={moderation.images}
          sortedRows={moderation.images}
          columns={COLUMNS}
          columnLabels={COLUMN_LABELS}
          sortableColumns={SORTABLE_COLUMNS}
          sortConfig={moderation.sortConfig}
          onToggleSort={moderation.toggleSort}
          tableClassName="platformImageModerationTable"
          mobileVisibleColumns={["platform_name", "thumbnail", "status"]}
          getRowKey={(image) => image.id}
          getCellValue={(image, column) => image[column]}
          formatCellValue={(column, value, image) => formatCellValue(column, value, image, moderation)}
          renderRowActions={(image) => renderRowActions(image, moderation)}
          pagination={{
            page: moderation.pageInfo.page,
            size: moderation.pageInfo.size,
            totalElements: moderation.pageInfo.totalElements,
            totalPages: moderation.pageInfo.totalPages,
            sizeOptions: moderation.pageSizeOptions,
            isLoading: moderation.isLoading,
            onPageChange: moderation.setPage,
            onSizeChange: moderation.setSize,
          }}
        />
      ) : null}

      {moderation.selectedPreviewImage ? (
        <ImagePreviewDialog
          image={moderation.selectedPreviewImage}
          onClose={moderation.closePreview}
        />
      ) : null}
    </section>
  );
}

/**
 * Formate une cellule du tableau de moderation.
 *
 * @param {string} column - Colonne en cours de rendu.
 * @param {unknown} value - Valeur brute de la cellule.
 * @param {Object} image - Ligne image complete.
 * @param {Object} moderation - Etat et actions de moderation.
 * @returns {string|import("react").JSX.Element} Cellule formatee.
 * @throws {void} Ne leve pas d'exception.
 */
function formatCellValue(column, value, image, moderation) {
  if (column === "thumbnail") {
    return (
      <button
        type="button"
        className="platformImageThumbnailButton"
        onClick={() => moderation.openPreview(image)}
        aria-label={`Voir l'image ${image.id} en grand`}
      >
        <img src={buildImageUrl(image)} alt="" loading="lazy" />
      </button>
    );
  }
  if (column === "status") {
    return (
      <span className={`platformImageStatusBadge ${String(value || "").toLowerCase()}`}>
        {STATUS_LABELS[value] || value || "-"}
      </span>
    );
  }
  if (column === "creation_date") {
    return formatDate(value);
  }
  return value || "-";
}

/**
 * Rend les boutons d'action d'une ligne d'image.
 *
 * @param {Object} image - Image de plateforme a moderer.
 * @param {Object} moderation - Etat et actions de moderation.
 * @returns {import("react").JSX.Element} Boutons d'action de moderation.
 * @throws {void} Ne leve pas d'exception.
 */
function renderRowActions(image, moderation) {
  const isUpdating = moderation.updatingImageId === image.id;
  const isAccepted = image.status === "ACCEPTED";
  const isMain = image.type === "MAIN";

  return (
    <div className="platformImageModerationActions">
      <button
        type="button"
        onClick={() => moderation.acceptImage(image)}
        disabled={!moderation.canUpdateStatus || isUpdating || isAccepted}
      >
        Accepter
      </button>
      <button
        type="button"
        className="dangerButton"
        onClick={() => moderation.refuseImage(image)}
        disabled={!moderation.canUpdateStatus || isUpdating}
      >
        Refuser
      </button>
      <button
        type="button"
        className="secondaryButton"
        onClick={() => moderation.setMainImage(image)}
        disabled={!moderation.canUpdateType || isUpdating || isMain}
      >
        MAIN
      </button>
    </div>
  );
}

/**
 * Affiche une image de plateforme dans une modale.
 *
 * @param {Object} props - Image et callback de fermeture.
 * @returns {import("react").JSX.Element} Dialogue d'aperçu.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function ImagePreviewDialog({ image, onClose }) {
  return (
    <div className="platformImagePreviewOverlay" role="presentation" onClick={onClose}>
      <div
        className="platformImagePreviewDialog"
        role="dialog"
        aria-modal="true"
        aria-label={`Image de plateforme ${image.platform_name || image.platform_id}`}
        onClick={(event) => event.stopPropagation()}
      >
        <button type="button" onClick={onClose} aria-label="Fermer l'aperçu">
          Fermer
        </button>
        <img src={buildImageUrl(image)} alt="" />
      </div>
    </div>
  );
}

/**
 * Construit l'URL d'affichage avec cache-busting local.
 *
 * @param {Object} image - Image de plateforme.
 * @returns {string} URL exploitable par une balise image.
 * @throws {void} Ne leve pas d'exception.
 */
function buildImageUrl(image) {
  const separator = String(image.image_url || "").includes("?") ? "&" : "?";
  return `${image.image_url || ""}${separator}v=${encodeURIComponent(image.id)}`;
}

/**
 * Formate une date ISO en libelle local.
 *
 * @param {string} value - Date brute retournee par le backend.
 * @returns {string} Date lisible ou tiret.
 * @throws {void} Ne leve pas d'exception.
 */
function formatDate(value) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString("fr-FR");
}

export default PlatformImageModerationSection;
