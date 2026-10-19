# Journal — 09-atelier-freelance

*Une ligne par avancée, la plus récente en bas.*

| Date | Avancement |
|---|---|
| 2026-09-17 | **Atelier né** (SOP-01 : test anti-refuge passé, 3 rondes de frontière, PRD validé par Zakaria). Forme retenue : un atelier, des chantiers — même grammaire que le 08. Règle de frontière actée : gratuit = Labo, facturé = BDW. Point d'arrêt : 2026-12-17. |
| 2026-09-17 | **Chantier 01 construit** — bot Telegram d'accompagnement Stake : parcours 5 étapes (VPN optionnel, compte, vérification, dépôt, premiers pas), boutons « C'est fait » / « Je bloque », mémoire de progression SQLite, emplacements vidéo prêts. Textes séparés du code (`contenu.py`) pour relecture par le demandeur. 15 tests verts, parcours prouvé au terminal. Pas déployé : attend le jeton et le lien de parrainage de Sofiane. |
| 2026-09-17 | **Contre-audit du chantier 01 passé, 6 défauts sérieux corrigés** — tous dans `bot.py`, le fichier sans tests. Décisions redescendues dans `parcours.py`, handlers testés avec un faux Telegram. 40 tests (8 ignorés hors conteneur). |
| 2026-09-19 | **Chantier 01, point mise en ligne** : code prêt, VPS vide. Sofiane injoignable ; il avait envoyé deux liens de parrainage d'influenceurs (pas le sien) et des photos d'eux. Décision Zakaria : **le jeton, il le crée lui-même chez @BotFather, propriété transférée à Sofiane ensuite**. Manquent encore : le lien à retenir, le VPN. |
| 2026-09-19 | **Chantier 01 en attente** (décision Zakaria) : on ne continue pas avant l'appel avec Sofiane. Point d'arrêt 2026-10-01 inchangé. |
| 2026-09-19 | Chantier 01 : Sofiane relancé sur le groupe (20:34, via le pont WhatsApp du 05, avec mention), appel à 20:35 (Pocket → transcrit par le 03, Pocket n'ayant pas fini), ses bonus reçus en privé → **V1.1 construite le soir même** (deux routes, crypto, bonus, Windscribe, un bot par influenceur), 56 tests. Prochaine action : les deux jetons BotFather. |
| 2026-09-19 | Chantier 01 **en ligne à 21:14** sur le VPS Labo : @guide_stake_jd_bot et @guide_stake_clive_bot (jetons BotFather créés par Zakaria), veilleur branché. Phase démo, admin = Zakaria ; décision : après validation, Sofiane héberge lui-même. |
| 2026-10-19 | Chantier 01, **V1.2 — les vidéos** : le groupe WhatsApp relu en entier (pont du 05), cinq vidéos du monteur repérées et quatre vérifiées image par image ; le bot gagne la pose des vidéos par l'administrateur depuis son téléphone (vidéo + mot de l'étape, `/videos`), l'étape VPN dit Hong Kong. 71 tests verts. Reste à Zakaria : pousser, poser les vidéos dans les deux bots, répondre au groupe. |
| 2026-10-19 | Chantier 01 : V1.2 en ligne, cinq vidéos posées dans les deux bots par Zakaria (5 ✔ chacun), groupe prévenu. On attend la relecture des textes par Sofiane. |
