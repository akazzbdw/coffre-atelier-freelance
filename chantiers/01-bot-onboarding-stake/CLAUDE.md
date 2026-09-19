# Chantier 01 — Bot Telegram d'accompagnement Stake

**Statut** : brief validé par Zakaria le 2026-09-17 · V1 construite · **V1.1 construite le 2026-09-19 d'après l'appel avec Sofiane** (deux routes, Windscribe, bonus, un bot par influenceur — 56 tests) · **prête à mettre en ligne** : il manque les deux jetons BotFather (Zakaria les crée, guide ci-dessous). Point d'arrêt inchangé : 2026-10-01.
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

## V1.1 — ce que l'appel du 2026-09-19 a changé (Sofiane, 20:35, 4 min 52, transcrit par le 03)

- **Deux routes**, question posée dès le départ : « Je pars de zéro » (VPN + création du compte + vérification + **achat de crypto** + dépôt) ou « J'ai déjà de la crypto » (question VPN, puis compte, vérification, dépôt). Sofiane : « soit il a rien — pas de VPN, pas de compte — soit il a déjà de la crypto ».
- **VPN = Windscribe** (gratuit, épelé par Sofiane).
- **Étape « Activer ton bonus »** après le dépôt, d'après le message privé de Sofiane (19/09, 20:40) : bonus 20 € (dépôt ≥ 20 € joué → 20 € de recharge) ou bonus 200 % (dépôt 200–1 000 €, à miser 35 fois, activé à la main sous 24 h, ne pas toucher au solde avant). Bouton **« Je demande mon bonus »** → demande enregistrée en base, l'administrateur (`TELEGRAM_ADMIN_CHAT_ID` : Zakaria d'abord, Sofiane ensuite) reçoit un message et transmet à l'équipe de Sofiane sur WhatsApp (« s'il y a peu de demandes, envoyez-les nous ici ; beaucoup → un bot »). Le bouton « Je passe cette étape » existe.
- **Un bot par influenceur** (« c'est pas le même canal, pas le même lien ») : deux influenceurs aujourd'hui, **JD** (`stake.jp/?c=YukkMZRj`) et **Clive** (`stake.jp/?c=YRu9cbAn`) — même code, deux conteneurs (`bot-jd`, `bot-clive`), deux `.env`, deux bases.
- **Qui fait quoi** : Zakaria crée les bots chez @BotFather et transfère la propriété ; **James** (équipe Sofiane) installe le bouton sur chaque canal ; **Julien** (monteur) fait les vidéos. Prochaine étape convenue : Zakaria connecte les bots, montre un faux canal, puis on itère sur leurs retours.
- Les textes des étapes crypto et bonus sont écrits par Claude d'après ces éléments : **à faire relire par Sofiane** comme les autres (`pipeline/contenu.py`).

### Mise en ligne (guide pour Zakaria)

1. Dans Telegram, ouvrir **@BotFather** → `/newbot` → nom affiché (ex. « Guide Stake JD ») → identifiant finissant par `bot` (ex. `guide_stake_jd_bot`) → BotFather renvoie le **jeton**. Refaire pour Clive.
2. Optionnel mais propre : `/setdescription`, `/setuserpic` (photo fournie par Sofiane).
3. Sur le VPS, dans `pipeline/` du chantier : copier `.env.example` en `.env.jd` et `.env.clive`, remplir `BOT_NOM`, `TELEGRAM_BOT_TOKEN`, `STAKE_LIEN_PARRAINAGE`, `TELEGRAM_ADMIN_CHAT_ID` (l'identifiant Telegram de Zakaria, celui que connaît le bot 05).
4. Ajouter le dossier à `PROJECTS` du veilleur `~/autodeploy.sh`, pousser : les deux conteneurs se construisent.
5. Preuve : `/start` sur chaque bot depuis le téléphone, une demande de bonus → le message admin arrive.
6. Plus tard, quand Sofiane répond : BotFather → `/mybots` → le bot → **Transfer Ownership** ; `TELEGRAM_ADMIN_CHAT_ID` passe à son identifiant.

## Exclu volontairement de la V1

- Les vidéos elles-mêmes (elles dépendent du monteur — leur emplacement est prêt, la V1 ne les attend pas).
- Tout suivi de qui s'est inscrit / qui a déposé (relève de l'espace affilié de Stake, pas du bot).
- Toute relance automatique des inactifs.
- Le multilingue : français seulement.

## Ce qu'on attend de Sofiane (bloquant pour la mise en ligne, pas pour la construction)

- [x] ~~**Quel lien de parrainage**~~ → **tranché à l'appel du 19/09 : les deux, un bot par influenceur** (JD et Clive, liens reçus le 17/09).
- [x] ~~Le bot créé chez @BotFather sur son compte~~ → **décision Zakaria du 2026-09-19 : Zakaria crée le bot chez @BotFather lui-même pour débloquer (Sofiane injoignable depuis le 17/09 23:03), puis lui transfère la propriété** (BotFather → `/mybots` → Transfer Ownership). Le garde-fou « le bot appartient à Sofiane » tient : c'est l'état d'arrivée, pas celui de départ.
- [x] ~~**Quel VPN gratuit**~~ → **Windscribe** (appel du 19/09).
- [x] ~~L'« offre à caler le long du processus »~~ → **reçue le 19/09 (20:40) : les deux bonus de bienvenue**, devenus l'étape « Activer ton bonus ».
- [ ] Sa relecture des textes des 7 étapes (écrits par Claude, validés par Zakaria) — surtout crypto et bonus, écrits d'après l'appel.
- [ ] Son identifiant Telegram, le jour du transfert (pour recevoir les demandes de bonus).

## Ce qu'on attend du monteur

- [ ] Une vidéo par étape, **verticale, 60 secondes maximum**, sans musique dominante, une seule action montrée à l'écran.
- [ ] Livrées en fichiers (pas de lien) — elles vivront dans Telegram.

## Garde-fous

- **Le bot appartient à Sofiane** : à son nom, sur son compte — créé par Zakaria le temps de le mettre en ligne, **propriété transférée à Sofiane dès qu'il répond** (décision 2026-09-19). Zakaria n'héberge que l'exécution. Rien lié au casino n'est enregistré au nom de Zakaria.
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
| 2026-09-19 | **Point mise en ligne** : code prêt (40 tests verts), rien sur le VPS (`.env` absent, pas dans le veilleur). Sofiane injoignable depuis le 17/09 (appel du 19/09 sans réponse). **Décision Zakaria : il crée le jeton chez @BotFather lui-même, propriété transférée à Sofiane ensuite.** Restent à trancher par Sofiane : lequel des deux liens de parrainage (JD ou Clive), le VPN. |
| 2026-09-19 | **Appel Sofiane 20:35 (après relance sur le groupe à 20:34, message envoyé par le bot 05 avec mention)** → **V1.1 construite le soir même** : question de départ (deux routes), étape crypto pour les débutants, étape bonus (deux bonus, demande → admin Telegram), Windscribe, un bot par influenceur (compose à deux services, `BOT_NOM`), colonne `debutant` ajoutée sans perte à une base V1. 56 tests verts (parcours + handlers, bibliothèque Telegram dans un venv de test), parcours débutant rejoué au terminal. Reste : les deux jetons BotFather (Zakaria). |
| 2026-09-17 | **Contre-audit passé et défauts corrigés** (6 sérieux, tous dans `bot.py`, qu'aucun test ne touchait). Les décisions du parcours sont redescendues dans `parcours.py`, sous tests ; `bot.py` a les siens (faux Telegram). 40 tests. |

## Ce que le contre-audit a trouvé (2026-09-17) et ce qu'on en a fait

Le premier jet marchait au terminal et passait ses 15 tests — et il aurait mal servi de vrais clients. Les six défauts sérieux vivaient tous dans `bot.py`, le seul fichier qu'aucun test ne touchait. Leçon gravée ici : **les tests suivaient la logique facile à tester, pas celle qui casse**.

| Ce qui cassait | Effet pour la personne | Corrigé par |
|---|---|---|
| `.env` copié mais laissé vide : la variable existe et vaut `""`, donc le garde-fou ne voyait pas le placeholder | le bot démarrait « en réel » et envoyait « Ouvre ce lien : » suivi de **rien** | `config_incomplete()` teste le vide, le commentaire et la forme (`http…`) ; `.env.example` sans valeur collée |
| `query.message.reply_text` sur un message trop vieux (Telegram renvoie un `InaccessibleMessage`) | quelqu'un qui revient 3 jours après et clique sur le bouton resté à l'écran : **aucune réponse, jamais** | tout passe par `ctx.bot.send_message` |
| `answer()` non protégé : « query is too old » au redémarrage du conteneur | le clic est perdu, la progression n'avance plus | `try/except` — le clic continue d'être traité |
| `suivante()` sur une étape qui n'est plus dans la liste | `ValueError`, handler mort, silence définitif | on se fie à l'étape **en base**, jamais au bouton cliqué |
| Vieux boutons restés dans le fil | retour en arrière de deux étapes, ou état « fini ET à l'étape 1 » | clic périmé = le bot le dit, l'état ne bouge pas ; le clavier du message traité est retiré |
| Étape renommée dans `contenu.py` (fichier relu par le demandeur) | cul-de-sac muet : « Tu en étais là : » puis rien, à chaque `/start` | `etat_utilisable()` répare l'état |
| Accolade tapée dans un texte (« appuie sur {Connect} ») | `KeyError`, l'étape ne partait jamais | plus de `.format()` : substitution de `{lien}` et `{vpn}` seulement |
| Aide longue > 4096 caractères | erreur 400, rien ne part | découpage automatique |
| Boîte noire écrite dans la couche éphémère du conteneur | toutes les traces perdues à chaque redéploiement, **y compris l'échec de démarrage** | `01-Vault` monté en écriture dans le compose |

Restent volontairement en l'état : les connexions SQLite ouvertes à chaque clic sont maintenant refermées, et `Application` traite les updates une par une (pas de concurrence) — si quelqu'un active `concurrent_updates` un jour, `ecrire_etat` devra passer en transaction.
