FROM python:3.12-slim
# tzdata : heure suisse pour les logs (règle Labo, audit 2026-08-11)
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*
ARG LABO_FUSEAU=Europe/Zurich
ENV TZ=${LABO_FUSEAU}
# L'arborescence de l'image reproduit celle du dépôt : la boîte noire (montée
# en ro sur /labo-repo/00-Systeme) calcule les mêmes chemins relatifs qu'ailleurs.
WORKDIR /labo-repo/02-Projets/09-atelier-freelance/chantiers/01-bot-onboarding-stake
COPY pipeline/requirements.txt pipeline/
RUN pip install --no-cache-dir -r pipeline/requirements.txt
# versions.env ↔ requirements.txt : python-telegram-bot installé = PTB_VERSION, sinon le build casse
ARG PTB_VERSION
RUN pip show python-telegram-bot | grep -qx "Version: ${PTB_VERSION}" \
    || { echo "python-telegram-bot installé ≠ PTB_VERSION=${PTB_VERSION} (00-Systeme/versions.env ↔ requirements.txt)"; exit 1; }
COPY pipeline/contenu.py pipeline/parcours.py pipeline/bot.py pipeline/
VOLUME /data
# labo-tests : point d'entrée FIGÉ joué par l'auto-déploiement (fiche `tests = true`) — les tests du chantier
# dans l'image fraîche, dépôt monté /labo:ro, sans réseau, AVANT de remplacer le conteneur (forme fermée,
# audit externe 2026-09-22). Rouge = mise à jour refusée.
RUN printf '#!/bin/sh\ncd /labo && exec python3 -m unittest discover -s 02-Projets/09-atelier-freelance/chantiers/01-bot-onboarding-stake/pipeline/tests\n' \
    > /usr/local/bin/labo-tests && chmod +x /usr/local/bin/labo-tests
CMD ["python", "pipeline/bot.py"]
