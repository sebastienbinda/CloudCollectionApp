/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : page proprietaire de gestion des partages de collection.
 */
import PageLayout from "./PageLayout";
import ProgressBar from "./ProgressBar";
import getCollectionShareStatusPresentation from "../collectionSharePresentation";

/**
 * Formate une date ISO pour l'affichage local.
 *
 * @param {string} value - Date ISO retournee par le backend.
 * @returns {string} Date et heure lisibles, ou tiret en cas d'absence.
 * @throws {void} Ne leve pas d'exception.
 */
function formatShareDate(value) {
  if (!value) {
    return "-";
  }
  const parsedDate = new Date(value);
  return Number.isNaN(parsedDate.getTime()) ? String(value) : parsedDate.toLocaleString("fr-FR");
}

/**
 * Retourne les permissions lisibles d'un partage.
 *
 * @param {Object} permissions - Permissions backend du partage.
 * @returns {string} Liste concise des acces accordes.
 * @throws {void} Ne leve pas d'exception.
 */
function formatSharePermissions(permissions = {}) {
  const labels = [];
  if (permissions.collection) labels.push("Collection");
  if (permissions.wishlist) labels.push("Liste de souhaits");
  if (permissions.prices) labels.push("Prix");
  return labels.join(", ") || "Aucun acces";
}

/**
 * Affiche le formulaire et les partages du proprietaire connecte.
 *
 * @param {Object} props - Session, navigation et etat du hook de partage.
 * @returns {import("react").JSX.Element} Page de gestion des partages.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function CollectionShareManagementView(props) {
  const management = props.collectionShareManagement;
  return (
    <PageLayout
      shellClassName="appShell collectionShareManagement"
      eyebrow="Collection"
      title="Partager ma collection"
      subtitle="Creez des acces temporaires et revoquez-les a tout moment."
      isAuthenticated={props.isAuthenticated}
      canUseCollectionViews={props.canUseCollectionViews}
      authenticatedUsername={props.authenticatedUsername}
      authenticatedProfile={props.authenticatedProfile}
      onOpenAbout={props.onOpenAbout}
      onOpenAuth={props.onOpenAuth}
      onOpenHome={props.onOpenHome}
      onOpenLibrary={props.onOpenLibrary}
      onOpenWishlist={props.onOpenWishlist}
      onOpenConfiguration={props.onOpenConfiguration}
      onLogout={props.onLogout}
    >
      {management.error ? <p className="error" role="alert">{management.error}</p> : null}
      {management.message ? <p className="success" role="status">{management.message}</p> : null}

      <section className="collectionShareFormSection" aria-labelledby="collection-share-form-title">
        <h2 id="collection-share-form-title">Nouveau partage</h2>
        <form className="collectionShareForm" onSubmit={management.createShare}>
          <label htmlFor="share-duration-hours">
            Duree de validite en heures
            <input
              id="share-duration-hours"
              type="number"
              min="1"
              max="240"
              step="1"
              required
              value={management.form.durationHours}
              onChange={(event) => management.updateForm("durationHours", event.target.value)}
            />
          </label>
          <fieldset>
            <legend>Permissions accordees</legend>
            <label>
              <input
                type="checkbox"
                checked={management.form.allowCollection}
                onChange={(event) => management.updateForm("allowCollection", event.target.checked)}
              />
              Jeux de la collection
            </label>
            <label>
              <input
                type="checkbox"
                checked={management.form.allowWishlist}
                onChange={(event) => management.updateForm("allowWishlist", event.target.checked)}
              />
              Liste de souhaits
            </label>
            <label>
              <input
                type="checkbox"
                checked={management.form.allowPrices}
                onChange={(event) => management.updateForm("allowPrices", event.target.checked)}
              />
              Informations de prix
            </label>
          </fieldset>
          <button
            type="submit"
            disabled={
              management.isCreating ||
              (!management.form.allowCollection && !management.form.allowWishlist)
            }
          >
            Creer le lien
          </button>
        </form>
      </section>

      <section className="collectionShareListSection" aria-labelledby="collection-share-list-title">
        <h2 id="collection-share-list-title">Partages existants</h2>
        {management.isLoading ? <ProgressBar label="Chargement des partages" /> : null}
        {!management.isLoading && management.shares.length === 0 ? (
          <p className="collectionShareEmptyState">Aucun partage n'a encore ete cree.</p>
        ) : null}
        <div className="collectionShareList">
          {management.shares.map((share) => {
            const statusPresentation = getCollectionShareStatusPresentation(share.status);
            const normalizedStatus = statusPresentation.key;
            return (
              <article
                className={`collectionShareCard collectionShareCard${normalizedStatus}`}
                key={share.id}
              >
                <div className="collectionShareCardHeader">
                  <h3>Partage #{share.id}</h3>
                  <span className={`collectionShareStatus collectionShareStatus${normalizedStatus}`}>
                    {statusPresentation.label}
                  </span>
                </div>
                <dl>
                  <div><dt>Cree le</dt><dd>{formatShareDate(share.created_at)}</dd></div>
                  <div><dt>Expire le</dt><dd>{formatShareDate(share.expires_at)}</dd></div>
                  <div><dt>Permissions</dt><dd>{formatSharePermissions(share.permissions)}</dd></div>
                </dl>
                <div className="collectionShareActions">
                  <button
                    className="secondaryButton"
                    type="button"
                    onClick={() => management.copyShareLink(share)}
                  >
                    Copier le lien
                  </button>
                  <button
                    className="dangerButton"
                    type="button"
                    disabled={normalizedStatus === "REVOKED" || management.revokingShareId === share.id}
                    onClick={() => management.revokeShare(share)}
                  >
                    Revoquer
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </PageLayout>
  );
}

export { formatShareDate, formatSharePermissions };
export default CollectionShareManagementView;
