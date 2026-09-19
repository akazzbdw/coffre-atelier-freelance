# Journal — 09-atelier-freelance

*Une ligne par avancée, la plus récente en bas.*

| Date | Avancement |
|---|---|
| 2026-09-17 | **Atelier né** (SOP-01 : test anti-refuge passé, 3 rondes de frontière, PRD validé par Zakaria). Forme retenue : un atelier, des chantiers — même grammaire que le 08. Règle de frontière actée : gratuit = Labo, facturé = BDW. Point d'arrêt : 2026-12-17. |
| 2026-09-17 | **Chantier 01 construit** — bot Telegram d'accompagnement Stake : parcours 5 étapes (VPN optionnel, compte, vérification, dépôt, premiers pas), boutons « C'est fait » / « Je bloque », mémoire de progression SQLite, emplacements vidéo prêts. Textes séparés du code (`contenu.py`) pour relecture par le demandeur. 15 tests verts, parcours prouvé au terminal. Pas déployé : attend le jeton et le lien de parrainage de Sofiane. |
| 2026-09-17 | **Contre-audit du chantier 01 passé, 6 défauts sérieux corrigés** — tous dans `bot.py`, le fichier sans tests. Décisions redescendues dans `parcours.py`, handlers testés avec un faux Telegram. 40 tests (8 ignorés hors conteneur). |
| 2026-09-19 | **Chantier 01, point mise en ligne** : code prêt, VPS vide. Sofiane injoignable ; il avait envoyé deux liens de parrainage d'influenceurs (pas le sien) et des photos d'eux. Décision Zakaria : **le jeton, il le crée lui-même chez @BotFather, propriété transférée à Sofiane ensuite**. Manquent encore : le lien à retenir, le VPN. |
