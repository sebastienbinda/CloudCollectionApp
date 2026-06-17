/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-06-17
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page publique de resultat de validation email.
 */
import PageLayout from "./PageLayout";

const RESULT_MESSAGES = {
  active: {
    title: "Compte actif",
    subtitle: "Votre adresse email est validee.",
    message: "Votre compte CloudCollectionApp est maintenant operationnel.",
    detail: "Vous pouvez vous connecter avec votre adresse email.",
    toneClassName: "success",
  },
  waiting_admin: {
    title: "Email valide",
    subtitle: "Votre adresse email est validee.",
    message: "Votre compte sera utilisable apres validation par un administrateur.",
    detail: "Vous recevrez un email lorsque votre compte sera active.",
    toneClassName: "success",
  },
  unavailable: {
    title: "Service indisponible",
    subtitle: "La validation email est temporairement indisponible.",
    message: "Votre demande n'a pas pu etre traitee pour le moment.",
    detail: "Vous pourrez reessayer depuis le lien recu par email.",
    toneClassName: "error",
  },
  error: {
    title: "Erreur de validation",
    subtitle: "Une erreur inattendue empeche la validation email.",
    message: "Votre demande n'a pas pu etre traitee.",
    detail: "Vous pourrez reessayer plus tard depuis le lien recu par email.",
    toneClassName: "error",
  },
  invalid: {
    title: "Validation impossible",
    subtitle: "Le lien de validation est invalide ou expire.",
    message: "Votre adresse email n'a pas ete validee avec ce lien.",
    detail: "Vous pouvez revenir a la page de connexion.",
    toneClassName: "error",
  },
};

/**
 * Retourne le contenu correspondant au statut de validation email.
 *
 * @returns {Object} Contenu affiche par la page.
 */
function getVerificationResultContent() {
  const params = new URLSearchParams(window.location.search);
  const status = params.get("status") || "invalid";
  return RESULT_MESSAGES[status] || RESULT_MESSAGES.invalid;
}

/**
 * Affiche le resultat public de validation email dans le layout applicatif.
 *
 * @param {Object} props - Etat de session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Page de resultat.
 */
function EmailVerificationResultView({
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenWishlist,
  onOpenConfiguration,
  onLogout,
}) {
  const content = getVerificationResultContent();

  return (
    <PageLayout
      shellClassName="container authContainer"
      eyebrow="Validation email"
      title={content.title}
      subtitle={content.subtitle}
      isAuthenticated={false}
      canUseCollectionViews={false}
      authenticatedUsername=""
      authenticatedProfile=""
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenWishlist={onOpenWishlist}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
      activeNavigationKey="login"
    >
      <section className="authForm" aria-labelledby="email-verification-result">
        <p id="email-verification-result" className={content.toneClassName}>
          {content.message}
        </p>
        <p>{content.detail}</p>
        <button type="button" onClick={onOpenAuth}>
          Se connecter
        </button>
      </section>
    </PageLayout>
  );
}

export default EmailVerificationResultView;
