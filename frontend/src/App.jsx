/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : point d'entree React principal de CloudCollectionApp.
 */
import AppFrame from "./components/AppFrame";
import AuthSessionModal from "./components/AuthSessionModal";
import AppViewSwitch from "./components/AppViewSwitch";
import useCloudCollectionViewModel from "./hooks/app/useCloudCollectionViewModel";

/**
 * Compose le cadre applicatif React principal.
 *
 * @returns {import("react").JSX.Element} Interface CloudCollectionApp.
 */
function App() {
  const { viewProps, authModalProps } = useCloudCollectionViewModel();

  return (
    <AppFrame>
      {AppViewSwitch.render(viewProps)}
      <AuthSessionModal {...authModalProps} />
    </AppFrame>
  );
}

export default App;
