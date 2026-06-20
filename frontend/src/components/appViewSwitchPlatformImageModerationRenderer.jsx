/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-20
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : rendu dedie de la page moderation images depuis AppViewSwitch.
 */
import PlatformImageModerationView from "./PlatformImageModerationView";

/**
 * Rend la page de moderation des images de plateformes.
 *
 * @param {Object} props - Etat applicatif et permissions de moderation.
 * @param {Object} pageLayoutProps - Proprietes communes du layout applicatif.
 * @returns {import("react").JSX.Element} Vue moderation images.
 * @throws {void} Ne leve pas d'exception pendant le rendu React.
 */
function renderPlatformImageModerationView(props, pageLayoutProps) {
  return (
    <PlatformImageModerationView
      {...pageLayoutProps}
      canModeratePlatformImages={props.actionPermissions.canModeratePlatformImages}
      platformImageModeration={props.platformImageModeration}
    />
  );
}

export default renderPlatformImageModerationView;
