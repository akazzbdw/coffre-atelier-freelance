"""Les textes que lit le client — SÉPARÉS du code, exprès.

Sofiane doit pouvoir relire et corriger ce fichier sans toucher au moteur :
un texte se change ici, le parcours ne bouge pas. Ton demandé (message du
2026-09-15) : « très soft, explications courtes, claires, on va droit au but
pour éviter de perdre ou de décourager le client ».

Règle du chantier : aucun conseil de jeu, aucune promesse de gain. Le bot
explique des démarches, il ne vend rien.
"""

# Placeholders : remplis par les réponses de Sofiane (variables d'environnement
# côté bot — voir bot.py). Tant qu'ils valent leur valeur par défaut, le bot
# refuse de démarrer en mode réel (jamais de lien mort envoyé à un client).
LIEN_PARRAINAGE_A_DEFINIR = "LIEN-PARRAINAGE-A-DEFINIR"
VPN_A_DEFINIR = "VPN-A-DEFINIR"

ACCUEIL = (
    "Salut 👋\n\n"
    "Je vais t'accompagner pas à pas pour ouvrir ton compte et commencer.\n"
    "C'est simple : une étape à la fois, tu avances à ton rythme.\n\n"
    "Tu peux t'arrêter quand tu veux — je me souviens où tu en es."
)

# V1.1 (appel Sofiane du 2026-09-19) : deux routes. « Je pars de zéro » =
# VPN + achat de crypto inclus d'office ; « J'ai déjà de la crypto » = VPN
# seulement si la personne dit en avoir besoin.
QUESTION_DEPART = (
    "Pour commencer, dis-moi où tu en es :\n\n"
    "• **Je pars de zéro** — pas de compte, pas de crypto : je te guide sur tout.\n"
    "• **J'ai déjà de la crypto** — on va plus vite."
)
BOUTON_ZERO = "Je pars de zéro"
BOUTON_CRYPTO = "J'ai déjà de la crypto"

QUESTION_VPN = (
    "Avant de commencer, une question :\n\n"
    "**Est-ce que tu as besoin d'un VPN ?**\n"
    "C'est une petite appli gratuite qui permet d'accéder au site si ton "
    "opérateur le bloque."
)

AIDE_VPN = (
    "Un VPN, c'est une appli gratuite à installer sur ton téléphone.\n\n"
    "Tu en as besoin si, en ouvrant le site, tu vois une page d'erreur ou "
    "« site inaccessible ».\n\n"
    "Si le site s'ouvre normalement chez toi, tu n'en as pas besoin."
)

# Chaque étape : un titre, un temps annoncé, un corps court, et une aide plus
# détaillée servie quand la personne appuie sur « Je bloque ».
ETAPES = [
    {
        "id": "vpn",
        "titre": "Installer le VPN",
        "minutes": 3,
        "optionnelle": True,          # servie seulement si la personne dit en avoir besoin
        "corps": (
            "1. Installe **{vpn}** (gratuit) depuis ton store d'applications\n"
            "2. Ouvre l'appli et choisis **Hong Kong** dans la liste des serveurs\n"
            "3. Appuie sur le gros bouton de connexion\n"
            "4. Attends le voyant vert, puis reviens ici"
        ),
        "aide": (
            "Deux choses qui bloquent le plus souvent :\n\n"
            "• **L'appli demande un abonnement** → cherche « continuer avec la "
            "version gratuite », c'est souvent écrit petit en bas.\n"
            "• **La connexion ne prend pas** → change de serveur dans la liste "
            "et réessaie.\n\n"
            "Si ça coince toujours, écris-moi ce que tu vois à l'écran."
        ),
    },
    {
        "id": "compte",
        "titre": "Créer ton compte",
        "minutes": 3,
        "corps": (
            "1. Ouvre ce lien : {lien}\n"
            "2. Renseigne ton e-mail et choisis un mot de passe\n"
            "3. Confirme l'e-mail que tu reçois\n\n"
            "⚠️ Utilise bien ce lien — c'est lui qui rattache ton compte."
        ),
        "aide": (
            "• **Tu ne reçois pas l'e-mail ?** Regarde dans les spams, puis "
            "demande un nouvel envoi depuis la page.\n"
            "• **« Cet e-mail existe déjà » ?** Tu as sans doute déjà un compte : "
            "connecte-toi plutôt, et passe à l'étape suivante.\n"
            "• **La page ne s'ouvre pas ?** C'est le cas où le VPN sert — dis-le "
            "moi, je te montre."
        ),
    },
    {
        "id": "verification",
        "titre": "Vérifier ton compte",
        "minutes": 5,
        "corps": (
            "1. Va dans ton profil, section **Vérification**\n"
            "2. Renseigne ton nom, ton prénom et ta date de naissance\n"
            "3. Prends en photo ta pièce d'identité, recto et verso\n\n"
            "C'est obligatoire pour pouvoir retirer de l'argent plus tard. "
            "Autant le faire maintenant, tranquillement."
        ),
        "aide": (
            "• **La photo est refusée ?** Pose le document à plat, en pleine "
            "lumière, sans flash, et vérifie que les 4 coins sont visibles.\n"
            "• **Ça prend du temps ?** La validation peut demander quelques "
            "heures. Tu peux continuer les étapes suivantes en attendant.\n"
            "• **On te demande un justificatif de domicile ?** Une facture ou "
            "un relevé de moins de 3 mois à ton nom suffit."
        ),
    },
    {
        "id": "crypto",
        "titre": "Acheter un peu de crypto",
        "minutes": 5,
        "debutants": True,            # servie seulement à qui part de zéro (V1.1)
        "corps": (
            "Le site fonctionne en crypto. Le plus simple, sans quitter le site :\n\n"
            "1. Clique sur **Wallet**, puis **Acheter des cryptos**\n"
            "2. Choisis le montant que tu as décidé — pas plus\n"
            "3. Paie par carte et attends que ça apparaisse dans ton wallet\n\n"
            "Ne mets que ce que tu peux te permettre de perdre."
        ),
        "aide": (
            "• **Ta carte est refusée ?** Certaines banques bloquent les achats de "
            "crypto : essaie une autre carte, ou passe par une appli d'achat "
            "(Coinbase, Binance…) puis envoie la crypto sur ton wallet du site.\n"
            "• **Quelle crypto choisir ?** Peu importe pour la suite — prends "
            "celle proposée par défaut, c'est la plus simple.\n"
            "• **Ça n'apparaît pas tout de suite ?** Quelques minutes sont "
            "normales. Ne repaie pas deux fois."
        ),
    },
    {
        "id": "depot",
        "titre": "Faire ton premier dépôt",
        "minutes": 4,
        "corps": (
            "1. Clique sur **Wallet**, puis **Dépôt**\n"
            "2. Choisis ton moyen de paiement\n"
            "3. Mets le montant que tu as décidé — pas plus\n\n"
            "Ne dépose que ce que tu peux te permettre de perdre."
        ),
        "aide": (
            "• **Ton moyen de paiement est refusé ?** Essaies-en un autre dans "
            "la liste, c'est fréquent selon les banques.\n"
            "• **Le dépôt n'apparaît pas tout de suite ?** Attends quelques "
            "minutes et rafraîchis la page avant de refaire l'opération — "
            "surtout ne dépose pas deux fois.\n"
            "• **Un code de confirmation t'est demandé ?** Il vient de ta "
            "banque, par SMS ou dans son appli."
        ),
    },
    {
        "id": "bonus",
        "titre": "Activer ton bonus de bienvenue",
        "minutes": 1,
        "corps": (
            "Au premier dépôt, tu as droit à **un** bonus, au choix :\n\n"
            "🎁 **Bonus 20 €** — tu as déposé au moins 20 € et tu les as joués : "
            "tu reçois 20 € de recharge.\n\n"
            "🎁 **Bonus 200 %** — tu as déposé entre 200 € et 1 000 € : le site "
            "ajoute 200 % de ton dépôt (200 € déposés → 400 € de bonus → 600 € au total). "
            "Ce total doit être misé 35 fois avant de pouvoir être retiré.\n\n"
            "⚠️ Le bonus n'est pas automatique : appuie sur **« Je demande mon bonus »**, "
            "l'équipe l'active sous 24 h. Pour le 200 %, **ne touche pas à ton solde** "
            "tant qu'il n'est pas activé.\n\n"
            "Tu peux aussi passer cette étape."
        ),
        "aide": (
            "• **Lequel choisir ?** Le 20 € si tu as fait un petit dépôt, le 200 % "
            "si tu as déposé au moins 200 €. Lis bien les conditions : elles "
            "engagent (le 200 % demande de miser 35 fois le total).\n"
            "• **Tu as déjà demandé ?** L'activation prend jusqu'à 24 h — pas besoin "
            "de redemander.\n"
            "• **Tu as touché à ton solde avant l'activation ?** Dis-le à Sofiane, "
            "il verra ce qui est possible."
        ),
    },
    {
        "id": "jeux",
        "titre": "Tes premiers pas",
        "minutes": 2,
        "corps": (
            "1. Depuis l'accueil, ouvre la section **Casino**\n"
            "2. Regarde d'abord, sans rien engager\n"
            "3. Commence petit, le temps de prendre tes repères\n\n"
            "Voilà, ton compte est prêt. 🎉"
        ),
        "aide": (
            "• **Tu ne sais pas par où commencer ?** Ouvre n'importe quel jeu et "
            "regarde une partie sans miser, juste pour voir comment ça marche.\n"
            "• **Une question sur un bonus ?** Les conditions sont écrites sur "
            "la page du bonus — lis-les avant de l'activer, elles engagent.\n\n"
            "Pour le reste, Sofiane peut te répondre directement."
        ),
    },
]

FIN = (
    "C'est terminé — tu as tout fait. 👌\n\n"
    "Si tu bloques sur quelque chose plus tard, reviens ici et tape /aide.\n"
    "Bonne route !"
)

RETOUR = "Content de te revoir. Tu en étais là :"
DEJA_FINI = "Tu as déjà terminé le parcours. Tape /recommencer si tu veux le refaire."
BOUTON_FAIT = "✅ C'est fait"
BOUTON_BLOQUE = "🤔 Je bloque"
BOUTON_OUI = "Oui, j'en ai besoin"
BOUTON_NON = "Non, ça marche chez moi"
BOUTON_CEST_QUOI = "C'est quoi un VPN ?"
BOUTON_BONUS = "🎁 Je demande mon bonus"
BOUTON_PASSER = "Je passe cette étape"
BONUS_DEMANDE_OK = (
    "C'est noté 👍 L'équipe active ton bonus sous 24 h.\n"
    "En attendant, ne touche pas à ton solde. On continue."
)
BONUS_DEJA_DEMANDE = "Ta demande est déjà partie — l'activation prend jusqu'à 24 h."
# ce que reçoit l'administrateur (Zakaria, puis Sofiane) à chaque demande
ADMIN_BONUS = "🎁 Demande de bonus — bot {bot}\nQui : {qui}\nÀ activer sous 24 h."

# Les vidéos (2026-10-19) : l'administrateur envoie une vidéo au bot avec, en légende, le mot
# de l'étape ; le bot la garde et la sert à chaque /start. Personne d'autre ne voit ces textes.
VIDEO_ENREGISTREE = "✔ Vidéo enregistrée pour « {titre} » ({etape}). Elle part avec cette étape dès maintenant."
VIDEO_ETAPE_INCONNUE = (
    "Je ne sais pas à quelle étape va cette vidéo. Renvoie-la avec, en légende, un de ces mots :\n{liste}")
VIDEO_PAS_UNE_VIDEO = "Ce fichier n'est pas une vidéo. Envoie-la « en tant que vidéo » (ou un fichier .mp4)."
VIDEOS_ETAT = ("Vidéos de ce bot :\n{lignes}\n\n"
               "Pour en poser ou en remplacer une : envoie-moi la vidéo avec, en légende, le mot de l'étape.")
APRES_AIDE = "Dis-moi quand c'est bon 👇"

# Réponses aux gestes « hors parcours » (contre-audit 2026-09-17 : un vieux
# bouton cliqué plus haut dans le fil ne doit jamais laisser le bot muet,
# ni faire reculer la personne).
DEJA_VALIDE = "Cette étape est déjà validée 👍 Tu en es à la suivante, plus haut."
DEJA_REPONDU = "Tu as déjà répondu à cette question — continue là où tu en étais 👆"
PLUS_DANS_LE_PARCOURS = "Tape /start pour (re)prendre le parcours."
PANNE = ("Aïe, j'ai eu un souci de mon côté. Réessaie dans un instant — "
         "et si ça recommence, tape /start.")
