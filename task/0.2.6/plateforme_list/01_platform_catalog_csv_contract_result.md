# 01 - Resultat contrat catalogue plateformes et CSV

## Perimetre

Cette tache stabilise le contrat de donnees du fichier :

```text
task/0.2.6/plateforme_list/consoles_jeux_video.csv
```

Elle ne modifie pas le code applicatif. Le resultat doit etre repris par la
tache `02_database_platform_schema_and_seed.md`.

## Validation Du CSV

Validations executees :

- lecture du CSV avec le module standard `csv` ;
- verification des colonnes attendues ;
- verification du nombre de colonnes par ligne ;
- verification des noms de plateformes vides ;
- verification des fabricants vides ;
- verification du format des dates ;
- verification de la validite reelle des dates parsees ;
- detection de doublons fonctionnels avec une cle compacte.

Resultats :

- lignes de donnees : `226` ;
- colonnes : `nom_machine`, `nom_fabricant`, `date_mise_en_vente`,
  `date_retrait_vente` ;
- lignes avec nombre de colonnes invalide : `0` ;
- noms de plateformes vides : `0` ;
- fabricants vides : `0` ;
- dates invalides : `0` ;
- valeur `En vente` dans `date_mise_en_vente` : `0` ;
- valeur `Inconnue` dans `date_mise_en_vente` : `0`.

Un doublon a ete detecte uniquement avec une cle tres compacte :

- `Atari 7800`
- `Atari 7800+`

Ce n'est pas un doublon bloquant. Le suffixe `+` distingue une machine
commerciale differente. La cle de chargement du catalogue ne doit donc pas
supprimer les suffixes significatifs comme `+`.

## Colonnes Source

Le CSV doit rester strictement compose des colonnes suivantes :

| Colonne CSV | Obligatoire | Description |
| --- | --- | --- |
| `nom_machine` | Oui | Nom public de la console ou plateforme. |
| `nom_fabricant` | Oui | Fabricant ou groupe de fabricants. |
| `date_mise_en_vente` | Oui | Date de commercialisation connue. |
| `date_retrait_vente` | Oui | Date de retrait, `Inconnue` ou `En vente`. |

Toute ligne sans `nom_machine` doit etre refusee.

## Mapping Vers `t_platform`

Mapping cible :

| CSV | Base | Regle |
| --- | --- | --- |
| `nom_machine` | `t_platform.name` | Texte trimme, conserve tel quel pour l'affichage. |
| `nom_fabricant` | `t_platform.manufacturer` | Texte trimme, conserve tel quel pour l'affichage. |
| `date_mise_en_vente` | `t_platform.release_date` | Date parse selon les regles ci-dessous. |
| `date_retrait_vente` | `t_platform.end_date` | Date parse selon les regles ci-dessous. |
| aucune colonne | `t_platform.description` | `{}` par defaut. |

La colonne `description` doit recevoir un objet JSON vide `{}` par defaut afin
de rester coherente avec le format API Bibliotheque existant, qui expose une
description structuree.

## Regles De Dates

Les dates du CSV acceptent trois niveaux de precision :

| Format CSV | Conversion SQL |
| --- | --- |
| `YYYY-MM-DD` | Date exacte a `00:00:00`. |
| `YYYY-MM` | Premier jour du mois a `00:00:00`. |
| `YYYY` | Premier janvier de l'annee a `00:00:00`. |

Valeurs speciales :

| Valeur | Colonne autorisee | Conversion SQL |
| --- | --- | --- |
| `Inconnue` | `date_mise_en_vente`, `date_retrait_vente` | `NULL`. |
| `En vente` | `date_retrait_vente` uniquement | `NULL`. |

`En vente` dans `date_mise_en_vente` doit etre refuse, car une plateforme sans
date de mise en vente connue doit utiliser `Inconnue`.

## Nullabilite Recommandee

La tache chapeau indique `release_date` et `manufacturer` comme non-null, mais
elle demande aussi de convertir les valeurs inconnues du CSV en `NULL`.

Contrat retenu pour les taches suivantes :

- `release_date` doit rester nullable ;
- `end_date` doit etre nullable ;
- `manufacturer` peut etre non-null si le CSV reste complet, mais il est plus
  robuste de le garder nullable en base comme dans le schema actuel ;
- `description` reste nullable dans le schema, mais le seed CSV insere `{}`.

## Cle De Chargement Du Catalogue

La cle de chargement du catalogue doit eviter les doublons sans fusionner des
machines differentes.

Regle recommandee :

- trim ;
- lowercase ;
- suppression des accents ;
- conservation des chiffres, lettres, espaces et signes significatifs tels que
  `+`, `/`, `-`, `.`.

La cle compacte utilisee pour le matching approximatif d'import ne doit pas etre
utilisee comme cle d'unicite du seed, car elle fusionnerait `Atari 7800` et
`Atari 7800+`.

## Corrections CSV

Aucune correction CSV n'est necessaire pour cette tache.

## Tests A Preparer Pour La Tache 02

Si une classe de parsing est creee, ajouter des tests couvrant :

- lecture des quatre colonnes attendues ;
- refus d'une colonne manquante ;
- refus d'un nom de machine vide ;
- parsing `YYYY-MM-DD` ;
- parsing `YYYY-MM` vers premier jour du mois ;
- parsing `YYYY` vers premier janvier ;
- conversion `Inconnue` vers `NULL` ;
- conversion `En vente` vers `NULL` uniquement pour `end_date` ;
- refus de `En vente` dans `release_date` ;
- conservation de `Atari 7800` et `Atari 7800+` comme deux plateformes
  distinctes.

## Decisions Pour Les Taches Suivantes

- Le seed doit charger `226` plateformes depuis le CSV actuel.
- Le seed doit etre idempotent.
- Le seed ne doit pas utiliser la cle compacte de fuzzy matching comme cle
  d'unicite.
- Les dates inconnues ne doivent pas etre remplacees par des fausses dates.
- `description` vaut `{}` par defaut pour les lignes CSV.
