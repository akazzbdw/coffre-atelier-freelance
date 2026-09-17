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
            "2. Ouvre l'appli et appuie sur le gros bouton de connexion\n"
            "3. Attends le voyant vert, puis reviens ici"
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
APRES_AIDE = "Dis-moi quand c'est bon 👇"

# Réponses aux gestes « hors parcours » (contre-audit 2026-09-17 : un vieux
# bouton cliqué plus haut dans le fil ne doit jamais laisser le bot muet,
# ni faire reculer la personne).
DEJA_VALIDE = "Cette étape est déjà validée 👍 Tu en es à la suivante, plus haut."
DEJA_REPONDU = "Tu as déjà répondu à cette question — continue là où tu en étais 👆"
PLUS_DANS_LE_PARCOURS = "Tape /start pour (re)prendre le parcours."
PANNE = ("Aïe, j'ai eu un souci de mon côté. Réessaie dans un instant — "
         "et si ça recommence, tape /start.")
