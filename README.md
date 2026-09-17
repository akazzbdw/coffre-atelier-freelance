# 09-atelier-freelance

**L'endroit unique où les demandes d'amis et de connaissances sont traitées, une par une.**

Une demande = un chantier dans `chantiers/`, avec son brief et son code.
Ce qui se réutilise d'un chantier à l'autre remonte dans `briques/`.

## Où regarder

| Je veux… | J'ouvre |
|---|---|
| savoir qui attend quoi | `CLAUDE.md` → tableau des demandes |
| les règles de l'atelier | `CLAUDE.md` |
| une demande précise | `chantiers/XX-nom/CLAUDE.md` |
| ce qui s'est passé | `JOURNAL.md` |

## Règle à ne pas oublier

Tant que c'est gratuit, ça vit ici. **À la première facture, ça part chez Blue Digital Works.**

## Chantier 01 — bot d'accompagnement Stake

```bash
cd chantiers/01-bot-onboarding-stake
python3 -m unittest discover -s pipeline/tests      # les tests
python3 pipeline/parcours.py --simuler              # rejouer le parcours au terminal
python3 pipeline/parcours.py --config               # ce qui manque avant la mise en ligne
```
