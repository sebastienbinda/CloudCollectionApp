/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | |__| (_) | | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-08-23
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : page dediee d'envoi de retours utilisateurs.
 */
import { useState } from "react";
import { ArrowRight, MessageSquare, Send } from "lucide-react";
import FeedbackApi from "../services/FeedbackApi";
import PageLayout from "./PageLayout";

/**
 * Affiche le formulaire de retour utilisateur envoye vers GitHub par le backend.
 *
 * @param {Object} props - Etat de session et callbacks de navigation.
 * @returns {import("react").JSX.Element} Page de retour utilisateur.
 */
function FeedbackView({
  isAuthenticated,
  isGuest,
  canUseCollectionViews,
  canViewCollection,
  canViewWishlist,
  canViewStatistics,
  canAccessConfiguration,
  authenticatedUsername,
  authenticatedProfile,
  onOpenAbout,
  onOpenAuth,
  onOpenHome,
  onOpenLibrary,
  onOpenFeedback,
  onOpenWishlist,
  onOpenStatistics,
  onOpenConfiguration,
  onLogout,
}) {
  const [feedbackCategory, setFeedbackCategory] = useState("idea");
  const [feedbackTitle, setFeedbackTitle] = useState("");
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackIssueUrl, setFeedbackIssueUrl] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [isSendingFeedback, setIsSendingFeedback] = useState(false);
  const canSubmitFeedback = isAuthenticated && !isGuest;

  const submitFeedback = async (event) => {
    event.preventDefault();
    setFeedbackStatus("");
    setFeedbackIssueUrl("");
    setFeedbackError("");
    setIsSendingFeedback(true);
    try {
      const feedback = await FeedbackApi.submitFeedback({
        category: feedbackCategory,
        title: feedbackTitle,
        message: feedbackMessage,
        page_url: window.location.href,
        user_agent: window.navigator.userAgent,
      });
      setFeedbackMessage("");
      setFeedbackTitle("");
      setFeedbackIssueUrl(feedback.issue_url || "");
      setFeedbackStatus("Merci, votre remarque a ete envoyee.");
    } catch (submitError) {
      setFeedbackError(submitError.message || "Impossible d'envoyer le retour.");
    } finally {
      setIsSendingFeedback(false);
    }
  };

  return (
    <PageLayout
      shellClassName="appShell feedbackShell"
      headerClassName="pageHeader feedbackHeader"
      eyebrow="Faire un retour"
      title="Aider le projet a progresser"
      subtitle="Signalez un probleme ou proposez une amelioration. Vous pourrez suivre votre demande apres l'envoi."
      isAuthenticated={isAuthenticated}
      canUseCollectionViews={canUseCollectionViews}
      canViewCollection={canViewCollection}
      canViewWishlist={canViewWishlist}
      canViewStatistics={canViewStatistics}
      canAccessConfiguration={canAccessConfiguration}
      authenticatedUsername={authenticatedUsername}
      authenticatedProfile={authenticatedProfile}
      onOpenAbout={onOpenAbout}
      onOpenAuth={onOpenAuth}
      onOpenHome={onOpenHome}
      onOpenLibrary={onOpenLibrary}
      onOpenFeedback={onOpenFeedback}
      onOpenWishlist={onOpenWishlist}
      onOpenStatistics={onOpenStatistics}
      onOpenConfiguration={onOpenConfiguration}
      onLogout={onLogout}
    >
      <section className="feedbackContent" aria-label="Faire un retour">
        <div className="aboutFeedbackPanel feedbackFormPanel">
          <span className="aboutCalloutIcon" aria-hidden="true">
            <MessageSquare size={26} strokeWidth={2.1} />
          </span>
          <h2>Envoyer une remarque</h2>
          <p>
            Decrivez simplement ce qui pose probleme ou ce qui pourrait etre ameliore. Une fois
            la remarque envoyee, un lien de suivi GitHub vous sera fourni.
          </p>
          {canSubmitFeedback ? (
            <form className="aboutFeedbackForm" onSubmit={submitFeedback}>
              <label>
                Type de retour
                <select
                  value={feedbackCategory}
                  onChange={(event) => setFeedbackCategory(event.target.value)}
                >
                  <option value="idea">Idee ou amelioration</option>
                  <option value="bug">Probleme rencontre</option>
                  <option value="usability">Utilisation peu claire</option>
                  <option value="other">Autre retour</option>
                </select>
              </label>
              <label>
                Titre court
                <input
                  type="text"
                  value={feedbackTitle}
                  maxLength={120}
                  onChange={(event) => setFeedbackTitle(event.target.value)}
                  placeholder="Exemple : le partage n'est pas clair"
                />
              </label>
              <label className="aboutFeedbackMessageField">
                Votre retour
                <textarea
                  value={feedbackMessage}
                  minLength={10}
                  maxLength={4000}
                  required
                  rows={5}
                  onChange={(event) => setFeedbackMessage(event.target.value)}
                  placeholder="Expliquez ce que vous avez remarque ou ce que vous aimeriez ameliorer."
                />
              </label>
              <button
                type="submit"
                className="aboutPrimaryAction"
                disabled={isSendingFeedback || feedbackMessage.trim().length < 10}
              >
                {isSendingFeedback ? "Envoi..." : "Envoyer le retour"}
                <Send size={18} strokeWidth={2.3} aria-hidden="true" />
              </button>
              {feedbackStatus ? (
                <p className="success feedbackSuccess">
                  <span>{feedbackStatus}</span>
                  {feedbackIssueUrl ? (
                    <a href={feedbackIssueUrl} target="_blank" rel="noreferrer">
                      Suivre ma demande sur GitHub
                    </a>
                  ) : null}
                </p>
              ) : null}
              {feedbackError ? <p className="error" role="alert">{feedbackError}</p> : null}
            </form>
          ) : (
            <div className="aboutFeedbackSignin">
              <p>
                Connectez-vous avec votre compte applicatif pour envoyer une remarque et obtenir
                un lien de suivi, sans creer de compte GitHub.
              </p>
              <button type="button" className="aboutPrimaryAction" onClick={onOpenAuth}>
                Se connecter pour faire un retour
                <ArrowRight size={18} strokeWidth={2.3} aria-hidden="true" />
              </button>
            </div>
          )}
        </div>
      </section>
    </PageLayout>
  );
}

export default FeedbackView;
