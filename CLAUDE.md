# 09-atelier-freelance — CLAUDE.md

**Statut** : actif
**Démarré** : 2026-09-17

## C'est quoi

Les demandes que des amis et des connaissances adressent à Zakaria (« tu peux me faire un bot Telegram ? », « tu peux me faire un site ? ») arrivaient en désordre, dans des groupes WhatsApp, et se perdaient. L'atelier est **l'endroit unique où elles sont traitées, une par une**.

Chaque demande devient un **chantier** dans `chantiers/`, avec son mini-brief et son code. Ce qui se réutilise d'un chantier à l'autre remonte dans `briques/`. L'atelier n'est pas une machine : c'est un dossier et un tableau.

Même grammaire que le **08-atelier-design** (un atelier, des chantiers) — et même garde-fou : on livre l'usage, on ne construit pas la machine qui traiterait « toutes les demandes futures ».

## La règle de frontière (actée le 2026-09-17)

**Tant que c'est un service d'ami, gratuit, ça vit au Labo. À la première facture, le dossier et le contact déménagent chez Blue Digital Works.**
Le code peut rester au Labo comme brique réutilisable ; les données du client, elles, partent. Cette règle se vérifie à chaque livraison — Claude la rappelle sans attendre qu'on lui demande.

Raison d'être : l'étanchéité du CLAUDE.md racine dit « clients = BDW ». Une demande gratuite d'un pote n'est pas encore un client ; une demande facturée l'est. La facture est le signal, parce qu'il est net et vérifiable.

## Version 1 minimale

Un dossier et **le tableau des demandes ci-dessous**. Aucune machine, aucun formulaire, aucune automatisation.
Zakaria dicte, Claude tient le tableau à jour dans le même commit que l'avancée.
L'outil se construira le jour où le tableau ne suffira plus — pas avant (leçon du 08, 2026-09-12).

## Exclu volontairement de la V1

- Pas de formulaire ni de bot d'entrée des demandes.
- Pas de détection automatique des demandes par la gare de triage (07) — à reposer quand le tableau saturera.
- Pas de fiche type, pas de devis type, pas de suivi de facturation (une demande facturée part chez BDW, donc ce suivi n'a pas sa place ici).

## Tableau des demandes

| Qui | Demande | Payé ? | Statut | Prochaine action |
|---|---|---|---|---|
| Sofiane El Mazghi | Bot Telegram qui accompagne pas à pas l'ouverture d'un compte Stake (chantier `01-bot-onboarding-stake`) | non — service d'ami | **en attente** (19/09) | attendre l'appel de Sofiane (injoignable depuis le 17/09) : lien à retenir, VPN, offre ; puis jeton BotFather par Zakaria et mise en ligne |

## Carte du projet

| Emplacement | Rôle |
|---|---|
| `CLAUDE.md` | Ce fichier : les règles de l'atelier + le tableau des demandes |
| `JOURNAL.md` | La mémoire : une ligne par avancée |
| `README.md` | Mode d'emploi rapide |
| `chantiers/` | Une demande = un chantier numéroté dedans (son `CLAUDE.md` de brief + son code) |
| `briques/` | Ce qui se réutilise d'un chantier à l'autre (extrait APRÈS coup, jamais anticipé) |
| `sorties/` | Ce que l'atelier produit (`AAAA-MM-JJ-type-nom`) |

*(Allègement assumé, règle 2026-08-11 : l'atelier n'a ni `app/` ni `api/` — il n'a pas d'interface. Un chantier qui a besoin d'une interface clone le squelette chez lui.)*

## Règles du projet

- **Une demande = un chantier numéroté** ; le numéro n'est jamais réutilisé.
- **Rien ne se construit sur un brief non validé** — un chantier a son `CLAUDE.md` de brief avant sa première ligne de code (SOP-01 transposée).
- **Le livrable appartient au demandeur** : quand c'est un bot, il est créé sur le compte du demandeur, Zakaria n'a que le jeton. On ne porte pas le risque d'une activité qui n'est pas la sienne.
- **Temps** : soirs et week-ends seulement. Si un chantier mord sur le sprint BDW des 90 jours, Claude le dit tranché et le chantier passe en pause.
- **Parité Mac ↔ Telegram** : l'atelier est du markdown versionné — le bot 05 le lit déjà. Chaque chantier dit dans son brief comment SA brique existe dans les deux mondes.
- **Boîte noire** : dès la première ligne de code d'un chantier, traçage via `00-Systeme/labo_trace.py` (runs, sorties, events).

## Critère d'arrêt

**Point d'arrêt : 2026-12-17.** Si à cette date aucune demande n'a été livrée ET utilisée par la personne qui l'a demandée, l'atelier part aux archives. Un chantier en cours de construction compte comme vivant ; un chantier qui attend une réponse depuis plus d'un mois ne compte pas.

## Journal

Le journal de l'atelier vit dans `JOURNAL.md` — une ligne par avancée, la plus récente en bas. Chaque chantier tient sa propre ligne de vie dans son dossier.
