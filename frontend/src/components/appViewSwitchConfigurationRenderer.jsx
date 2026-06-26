/*
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-24
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 * Description : rendu dedie de la page Configuration depuis AppViewSwitch.
 */
import ConfigurationView from "./ConfigurationView";

/**
 * Rend la page Configuration avec ses permissions et actions.
 *
 * @param {Object} props - Etat applicatif de Configuration.
 * @param {Object} pageLayoutProps - Proprietes communes du layout applicatif.
 * @returns {import("react").JSX.Element} Vue Configuration.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function renderConfigurationView(props, pageLayoutProps) {
  return (
    <ConfigurationView
      {...pageLayoutProps}
      username={props.authenticatedUsername}
      platforms={props.platforms}
      canAddGame={props.actionPermissions.canAddGame}
      canDownloadOds={props.actionPermissions.canDownloadOds}
      canResetLibrary={props.actionPermissions.canResetLibrary}
      canImportLibraryCsv={props.actionPermissions.canImportLibraryCsv}
      canSyncPlatformCatalog={props.actionPermissions.canSyncPlatformCatalog}
      canModeratePlatformImages={props.actionPermissions.canModeratePlatformImages}
      canReinitializeCollection={props.actionPermissions.canReinitializeCollection}
      canSearchUsers={props.actionPermissions.canSearchUsers}
      canManageCollectionShares={props.canManageCollectionShares}
      downloadError={props.downloadError}
      isDownloadingOds={props.isDownloadingOds}
      libraryResetError={props.libraryResetError}
      libraryResetMessage={props.libraryResetMessage}
      isResettingLibrary={props.isResettingLibrary}
      platformCatalogSyncError={props.platformCatalogSyncError}
      platformCatalogSyncMessage={props.platformCatalogSyncMessage}
      isSyncingPlatformCatalog={props.isSyncingPlatformCatalog}
      reinitializationError={props.reinitializationError}
      isReinitializingCollection={props.isReinitializingCollection}
      onAddGame={props.openAddGamePage}
      onOpenUsers={props.openUsersPage}
      onOpenAdminLibraryImport={props.openAdminLibraryImport}
      onOpenPlatformImageModeration={props.openPlatformImageModeration}
      onOpenCollectionOnboarding={props.openCollectionOnboarding}
      onOpenCollectionShares={props.openCollectionShares}
      onDownloadOds={props.downloadOdsFile}
      onResetLibrary={props.resetLibrary}
      onSyncPlatformCatalog={props.syncPlatformCatalog}
      onReinitializeCollection={props.reinitializeCollection}
    />
  );
}

export default renderConfigurationView;
