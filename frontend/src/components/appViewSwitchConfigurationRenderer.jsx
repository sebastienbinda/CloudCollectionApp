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
      isLibraryResetConfirmationOpen={props.isLibraryResetConfirmationOpen}
      waitingValidationResetCount={props.waitingValidationResetCount}
      platformCatalogSyncError={props.platformCatalogSyncError}
      platformCatalogSyncMessage={props.platformCatalogSyncMessage}
      isSyncingPlatformCatalog={props.isSyncingPlatformCatalog}
      reinitializationError={props.reinitializationError}
      isReinitializingCollection={props.isReinitializingCollection}
      onOpenUsers={props.openUsersPage}
      onOpenAdminLibraryImport={props.openAdminLibraryImport}
      onOpenPlatformImageModeration={props.openPlatformImageModeration}
      onOpenCollectionOnboarding={props.openCollectionOnboarding}
      onOpenCollectionShares={props.openCollectionShares}
      onDownloadOds={props.downloadOdsFile}
      onResetLibrary={props.resetLibrary}
      onCancelLibraryReset={props.cancelLibraryReset}
      onConfirmLibraryReset={props.confirmLibraryReset}
      onSyncPlatformCatalog={props.syncPlatformCatalog}
      onReinitializeCollection={props.reinitializeCollection}
    />
  );
}

export default renderConfigurationView;
