# Chantier 01 — Bot Telegram d'accompagnement Stake

**Statut** : brief validé par Zakaria le 2026-09-17 · V1 construite, en attente des réponses de Sofiane pour la mise en ligne
**Demandeur** : Sofiane El Mazghi — groupe WhatsApp « Bot telegram », créé le 2026-09-15
**Payé** : non, service d'ami → reste au Labo (règle de frontière de l'atelier)
**Ouvert** : 2026-09-17

## La demande, dans les mots de Sofiane (15/09, 20:49)

> L'idée serait de mettre en place un bot qui accompagne les clients tout au long du processus, de manière très simple et intuitive. Le bot devra les guider étape par étape : création du compte Stake ; vérification et configuration du compte ; dépôt ; accès aux jeux et premières étapes pour commencer. Si certaines étapes nécessitent une configuration technique, le bot pourra également orienter l'utilisateur vers les ressources appropriées. L'objectif est vraiment que le parcours soit très détaillé, mais toujours très soft, avec des explications courtes, claires et faciles à suivre. À chaque étape, on va droit au but pour éviter de perdre ou de décourager le client. L'idéal serait également d'avoir des tutos vidéo pour accompagner chaque étape. […] le bot doit pouvoir prendre le client par la main du début à la fin, avec un parcours fluide, simple et accessible, même pour quelqu'un qui n'est pas à l'aise avec ce type de démarche.

> Ah oui aussi l'installation du vpn pour ceux qui en ont besoin ! Il est gratuit. (15/09, 20:49)

Autres participants du groupe : un monteur vidéo (ajouté le 15/09 à 23:13, « j'attends toutes les infos ») et un collègue de Sofiane.

## À quoi ressemble la victoire

Une personne qui ne connaît rien à Stake ouvre le bot, suit le parcours sans jamais sortir de Telegram, et arrive au bout avec un compte créé via le lien de parrainage de Sofiane, vérifié, alimenté, prête à jouer — sans avoir eu besoin de poser une question à un humain.

## Version 1 minimale (livrable en une à deux soirées)

Un parcours guidé **en texte**, à étapes, dans Telegram :

0. *(branche optionnelle)* VPN — proposée seulement à qui répond en avoir besoin.
1. Création du compte Stake — **via le lien de parrainage de Sofiane**.
2. Vérification et configuration du compte.
3. Dépôt.
4. Accès aux jeux et premiers pas.

Mécanique :
- Une étape à la fois, explications courtes, ton soft, deux boutons : **« ✅ C'est fait »** et **« 🤔 Je bloque »**.
- **Mémoire de progression** : celui qui revient trois jours plus tard reprend exactement où il s'était arrêté.
- **Emplacement vidéo prêt à chaque étape** : le jour où le monteur livre, on dépose les fichiers, le parcours ne bouge pas.
- « Je bloque » → un message d'aide plus détaillé, puis la possibilité de contacter Sofiane.

## Exclu volontairement de la V1

- Les vidéos elles-mêmes (elles dépendent du monteur — leur emplacement est prêt, la V1 ne les attend pas).
- Tout suivi de qui s'est inscrit / qui a déposé (relève de l'espace affilié de Stake, pas du bot).
- Toute relance automatique des inactifs.
- Le multilingue : français seulement.

## Ce qu'on attend de Sofiane (bloquant pour la mise en ligne, pas pour la construction)

- [ ] Son **lien de parrainage Stake**.
- [ ] Le bot créé chez **@BotFather sur son compte** (nom + @ + image), et le **jeton** transmis à Zakaria en privé — jamais dans le groupe.
- [ ] **Quel VPN gratuit** il recommande (l'étape 0 reste vide sans ça).
- [ ] Sa relecture des textes des 5 étapes (écrits par Claude, validés par Zakaria, envoyés pour accord).

## Ce qu'on attend du monteur

- [ ] Une vidéo par étape, **verticale, 60 secondes maximum**, sans musique dominante, une seule action montrée à l'écran.
- [ ] Livrées en fichiers (pas de lien) — elles vivront dans Telegram.

## Garde-fous

- **Le bot appartient à Sofiane** : créé sur son compte, à son nom. Zakaria n'héberge que l'exécution. Rien lié au casino n'est enregistré au nom de Zakaria.
- **Réserve juridique notée, décision assumée** : en Suisse, la promotion de casinos en ligne non autorisés (LJAr) est un terrain exposé. Décision Zakaria du 2026-09-17 : **on avance, l'exploitation est l'affaire de Sofiane**. La réserve est écrite ici pour qu'elle ne se perde pas — elle se repose si l'activité devient facturée (donc BDW).
- **Aucun conseil de jeu, aucune promesse de gain** dans les textes du bot : il explique des démarches, il ne vend pas.
- **Jeton du bot** : variable d'environnement, jamais en clair, jamais sur GitHub.

## Stack

Python + `python-telegram-bot` · état de progression en SQLite · conteneur sur le VPS Labo (pattern du 05) · traçage `00-Systeme/labo_trace.py` dès la première ligne.
Pas d'interface web : allègement assumé, on ne clone que `pipeline/`.

## Parité Mac ↔ Telegram

Le chantier EST un bot Telegram — le monde Telegram est natif. Côté Mac : le parcours se rejoue en ligne de commande (`python3 pipeline/parcours.py --simuler`) pour écrire et relire les textes sans passer par Telegram, et les traces remontent dans la boîte noire des deux côtés.

## Critère d'arrêt

Si Sofiane ne fournit ni lien de parrainage ni jeton **avant le 2026-10-01**, le chantier passe en pause et sort du tableau des demandes actives. Un bot construit que personne ne met en ligne ne compte pas comme une livraison.

## Journal du chantier

| Date | Avancement |
|---|---|
| 2026-09-17 | Brief écrit d'après le groupe WhatsApp (lu via le pont OpenWA du 05). En attente de validation Zakaria. |
| 2026-09-17 | Parcours construit et prouvé au terminal (15 tests). En attente des trois réponses de Sofiane pour la mise en ligne. |
