#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-20
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Contrat des informations privees importables pour un jeu utilisateur."""

ALLOWED_PRICE_UNITS = frozenset({"EUR", "USD", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "KRW"})
ALLOWED_REGIONS = frozenset({
    "JAP", "US", "EU-FR", "EU-UK", "EU-DE", "EU-ES", "EU-IT",
    "AU", "ASIA", "KOR", "TWN", "HK", "CHN",
})
REGION_ALIASES_BY_VALUE = {
    "US": frozenset({"NTSC - US", "US - NTSC"}),
    "EU-FR": frozenset({"FR", "PAL - FR", "PAL - EUR", "EUR - PAL"}),
    "EU-UK": frozenset({"UK", "PAL - UK"}),
    "EU-DE": frozenset({"DE", "PAL - DE"}),
    "EU-ES": frozenset({"ES", "PAL - ES"}),
    "EU-IT": frozenset({"IT", "PAL - IT"}),
}
CONDITION_LABELS_BY_VALUE = {
    0: (
        "mauvais", "tres mauvais", "abime", "endommage", "use", "tres use",
        "bad", "poor", "damaged", "worn", "heavily worn",
    ),
    1: (
        "correct", "etat correct", "moyen", "etat moyen", "acceptable", "passable",
        "occasion", "fair", "fair condition", "average", "used",
    ),
    2: ("bon", "bon etat", "propre", "good", "good condition", "clean"),
    3: (
        "tres bon", "tres bon etat", "excellent", "excellent etat", "comme neuf",
        "very good", "very good condition", "near mint", "like new",
    ),
    4: (
        "neuf", "neuf sous blister", "scelle", "jamais utilise", "new", "brand new",
        "mint", "sealed", "factory sealed", "unused",
    ),
}
CONDITION_EXCLUDED_LABELS = frozenset({
    "complet", "complete", "complete in box", "loose", "loos", "cib",
})
BOOLEAN_TRUE_LABELS = frozenset({
    "oui", "o", "yes", "y", "true", "vrai", "1", "x", "✓", "present", "avec",
})
BOOLEAN_FALSE_LABELS = frozenset({
    "non", "n", "no", "false", "faux", "0", "absent", "sans",
})
BOOLEAN_MATCH_LIMIT = 75
