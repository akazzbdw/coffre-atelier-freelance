"""Le bot Telegram du chantier 01 — une PORTE, pas un cerveau.

Toutes les DÉCISIONS sont dans parcours.py (et sous tests) ; tous les TEXTES
dans contenu.py. Ici : Telegram, les boutons, et rien d'autre.

Le bot appartient à Sofiane (créé sur son compte @BotFather) ; Zakaria
n'héberge que l'exécution — garde-fou du CLAUDE.md du chantier.

Env requis : TELEGRAM_BOT_TOKEN, STAKE_LIEN_PARRAINAGE, VPN_NOM.
Env optionnel : MODE_TEST=1 (autorise le démarrage sans lien réel et montre
les emplacements vidéo), VIDEOS_JSON (chemin du fichier des vidéos),
BOT_NOM (l'influenceur servi — un bot par influenceur, V1.1),
TELEGRAM_ADMIN_CHAT_ID (qui reçoit les demandes de bonus : Zakaria d'abord,
Sofiane quand il aura le bot — sans lui, la demande est seulement tracée).
L'administrateur est aussi le seul à poser les vidéos (2026-10-19) : il envoie
une vidéo au bot avec, en légende, le mot de l'étape ; `/videos` dit ce qui est
en place. Décisions et fichier : parcours.py (« les vidéos »).

Durci le 2026-09-17 après contre-audit (SOP-01 Phase 5). Trois règles tenues
partout dans ce fichier :
  1. on répond TOUJOURS par `ctx.bot.send_message` — jamais `query.message.reply_*`,
     qui n'existe plus quand le message porteur du bouton est trop vieux ;
  2. on ne fait jamais confiance au bouton cliqué, seulement à l'état en base ;
  3. un handler ne meurt jamais en silence — au pire il dit quelque chose ;
     le filet de dernier recours est celui de tout le Labo (posé par le tronc
     commun `00-Systeme/labo_bot.py`, 2026-09-20 : une coupure Telegram n'est
     plus un « bot-echec » ; envoi, découpe et gras → HTML viennent aussi de lui).
"""

import logging
import os
import sys
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contenu  # noqa: E402
import parcours  # noqa: E402
from parcours import labo_bot  # noqa: E402  — 00-Systeme trouvé par parcours

log = logging.getLogger("bot-stake")

MODE_TEST = os.environ.get("MODE_TEST") == "1"


def videos() -> dict:
    """{id_etape: vidéo posée} — vide tant que l'administrateur n'a rien posé.
    Lecture et forme : parcours.videos_lire / parcours.video_pour."""
    return parcours.videos_lire()


def admin_id() -> str:
    return os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "").strip()


def est_admin(update: Update) -> bool:
    return bool(admin_id()) and str(update.effective_user.id) == admin_id()


en_html = labo_bot.telegram_html   # **gras** → <b>, le reste échappé (tronc commun)


def clavier_etape(etape_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(contenu.BOUTON_FAIT, callback_data=f"fait:{etape_id}"),
        InlineKeyboardButton(contenu.BOUTON_BLOQUE, callback_data=f"bloque:{etape_id}"),
    ]])


def clavier_depart() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(contenu.BOUTON_ZERO, callback_data="depart:zero")],
        [InlineKeyboardButton(contenu.BOUTON_CRYPTO, callback_data="depart:crypto")]])


def clavier_bonus() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(contenu.BOUTON_BONUS, callback_data="bonus:demande")],
        [InlineKeyboardButton(contenu.BOUTON_PASSER, callback_data="fait:bonus"),
         InlineKeyboardButton(contenu.BOUTON_BLOQUE, callback_data="bloque:bonus")]])


def clavier_pour(etape_id: str) -> InlineKeyboardMarkup:
    return clavier_bonus() if etape_id == "bonus" else clavier_etape(etape_id)


def clavier_vpn(complet: bool = True) -> InlineKeyboardMarkup:
    lignes = [[InlineKeyboardButton(contenu.BOUTON_OUI, callback_data="vpn:oui")],
              [InlineKeyboardButton(contenu.BOUTON_NON, callback_data="vpn:non")]]
    if complet:
        lignes.append([InlineKeyboardButton(contenu.BOUTON_CEST_QUOI,
                                            callback_data="vpn:quoi")])
    return InlineKeyboardMarkup(lignes)


async def dire(ctx, chat_id: int, texte: str, clavier=None) -> None:
    """Envoyer un texte, découpé si nécessaire — le clavier va sur le dernier
    morceau. Passe par ctx.bot : ne dépend jamais d'un message porteur."""
    await labo_bot.envoyer(ctx.bot, texte, chat_id=chat_id, clavier=clavier)


async def retirer_clavier(requete) -> None:
    """Le message qu'on vient de traiter ne doit plus proposer ses boutons."""
    try:
        await requete.edit_message_reply_markup(reply_markup=None)
    except TelegramError:
        pass          # message trop vieux ou déjà édité — sans conséquence


async def notifier_admin(ctx, texte: str) -> None:
    """Prévenir l'administrateur (demande de bonus). Jamais bloquant : sans
    identifiant, ou si Telegram refuse, la demande reste tracée en base et
    en boîte noire — elle n'est pas perdue, elle est juste à aller lire."""
    admin = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    if not admin:
        parcours.tracer("bonus-non-notifie", "TELEGRAM_ADMIN_CHAT_ID absent")
        return
    try:
        await ctx.bot.send_message(chat_id=int(admin), text=texte)
    except (TelegramError, ValueError) as e:
        log.error("admin injoignable (%s)", e)
        parcours.tracer("bonus-non-notifie", f"admin injoignable : {e}")


def nom_lisible(user) -> str:
    pseudo = getattr(user, "username", None)
    nom = " ".join(x for x in (getattr(user, "first_name", None),
                               getattr(user, "last_name", None)) if x)
    return (f"@{pseudo}" if pseudo else nom or "?") + f" (id {getattr(user, 'id', '?')})"


async def envoyer_etape(ctx, chat_id: int, personne: str, etape_id: str,
                        etat: dict) -> None:
    lien, vpn_nom = parcours.config()
    etapes = parcours.route(etat)
    etape = parcours.etape_par_id(etapes, etape_id)
    if etape is None:
        # ne peut plus arriver (etat_utilisable répare) — mais on ne se tait pas
        log.error("étape inconnue demandée : %s", etape_id)
        parcours.tracer("bot-echec", f"étape inconnue : {etape_id}")
        await dire(ctx, chat_id, contenu.DEJA_FINI)
        return
    texte = parcours.rendu(etape, lien, vpn_nom, parcours.position(etapes, etape_id))
    parcours.tracer("parcours-etape", f"{personne} · {etape_id}")
    video = parcours.video_pour(videos(), etape_id)
    if video:
        fichier, genre = video
        try:
            if genre == "document":
                await ctx.bot.send_document(chat_id=chat_id, document=fichier,
                                            caption=en_html(texte),
                                            parse_mode=ParseMode.HTML,
                                            reply_markup=clavier_pour(etape_id))
            else:
                await ctx.bot.send_video(chat_id=chat_id, video=fichier,
                                         caption=en_html(texte),
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=clavier_pour(etape_id))
            return
        except TelegramError as e:
            # une vidéo qui ne part pas ne doit pas priver de l'étape
            log.error("vidéo %s refusée (%s) — étape servie en texte", etape_id, e)
            parcours.tracer("bot-echec", f"vidéo {etape_id} refusée : {e}")
    if MODE_TEST:
        texte += f"\n\n[ 🎥 emplacement vidéo prêt — {etape_id} ]"
    await dire(ctx, chat_id, texte, clavier_pour(etape_id))


async def demarrer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    personne = str(update.effective_user.id)

    # on lit (et répare) l'état, puis on referme AVANT de parler à Telegram
    with parcours.connexion() as cx:
        etat = parcours.etat_utilisable(cx, personne)
        if not etat["fini"] and not etat["etape"]:
            parcours.ecrire_etat(cx, personne, vpn=None, etape=None, fini=False)

    if etat["fini"]:
        await dire(ctx, chat_id, contenu.DEJA_FINI)
        return
    if etat["etape"]:
        await dire(ctx, chat_id, contenu.RETOUR)
        parcours.tracer("parcours-reprise", personne)
        await envoyer_etape(ctx, chat_id, personne, etat["etape"], etat)
        return
    if etat["debutant"] is False:      # a répondu « déjà de la crypto », pas encore au VPN
        await dire(ctx, chat_id, contenu.QUESTION_VPN, clavier_vpn())
        return

    parcours.tracer("parcours-debut", personne)
    await dire(ctx, chat_id, contenu.ACCUEIL)
    await dire(ctx, chat_id, contenu.QUESTION_DEPART, clavier_depart())


async def bouton(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    requete = update.callback_query
    try:
        await requete.answer()
    except TelegramError:
        pass          # « query is too old » après un redémarrage : on continue
    chat_id = update.effective_chat.id
    personne = str(update.effective_user.id)
    action, _, valeur = (requete.data or "").partition(":")

    if action == "depart":
        suite, etape = parcours.choisir_depart(personne, valeur == "zero")
        await retirer_clavier(requete)
        if suite == "ignore":
            await dire(ctx, chat_id, contenu.DEJA_REPONDU)
            return
        if suite == "vpn":
            await dire(ctx, chat_id, contenu.QUESTION_VPN, clavier_vpn())
            return
        with parcours.connexion() as cx:
            etat = parcours.lire_etat(cx, personne)
        await envoyer_etape(ctx, chat_id, personne, etape, etat)
        return

    if action == "vpn":
        if valeur == "quoi":
            await dire(ctx, chat_id, contenu.AIDE_VPN, clavier_vpn(complet=False))
            return
        suite, etape = parcours.choisir_vpn(personne, valeur == "oui")
        await retirer_clavier(requete)
        if suite == "ignore":       # vieux bouton : on ne renvoie personne au début
            await dire(ctx, chat_id, contenu.DEJA_REPONDU)
            return
        with parcours.connexion() as cx:
            etat = parcours.lire_etat(cx, personne)
        await envoyer_etape(ctx, chat_id, personne, etape, etat)
        return

    if action == "bonus":
        suite, etape = parcours.demander_bonus(personne, nom_lisible(update.effective_user))
        if suite == "ignore":
            await dire(ctx, chat_id, contenu.DEJA_VALIDE)
            return
        if suite == "deja":
            await dire(ctx, chat_id, contenu.BONUS_DEJA_DEMANDE, clavier_bonus())
            return
        await retirer_clavier(requete)
        await notifier_admin(ctx, contenu.ADMIN_BONUS
                             .replace("{bot}", os.environ.get("BOT_NOM", "?"))
                             .replace("{qui}", nom_lisible(update.effective_user)))
        await dire(ctx, chat_id, contenu.BONUS_DEMANDE_OK)
        if etape is None:
            parcours.tracer("parcours-fin", personne)
            await dire(ctx, chat_id, contenu.FIN)
            return
        with parcours.connexion() as cx:
            etat = parcours.lire_etat(cx, personne)
        await envoyer_etape(ctx, chat_id, personne, etape, etat)
        return

    if action == "bloque":
        aide = parcours.aide_courante(personne)
        if aide is None:
            await dire(ctx, chat_id, contenu.PLUS_DANS_LE_PARCOURS)
            return
        etape_id, texte = aide
        await dire(ctx, chat_id, texte, clavier_pour(etape_id))
        await dire(ctx, chat_id, contenu.APRES_AIDE)
        parcours.tracer("parcours-blocage", f"{personne} · {etape_id}")
        return

    if action == "fait":
        suite, etape = parcours.avancer(personne, valeur)
        await retirer_clavier(requete)
        if suite == "ignore":
            await dire(ctx, chat_id, contenu.DEJA_VALIDE)
            return
        if suite == "fini":
            parcours.tracer("parcours-fin", personne)
            await dire(ctx, chat_id, contenu.FIN)
            return
        with parcours.connexion() as cx:
            etat = parcours.lire_etat(cx, personne)
        await envoyer_etape(ctx, chat_id, personne, etape, etat)


async def aide(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    aide_ = parcours.aide_courante(str(update.effective_user.id))
    if aide_ is None:
        await dire(ctx, chat_id, contenu.PLUS_DANS_LE_PARCOURS)
        return
    etape_id, texte = aide_
    await dire(ctx, chat_id, texte, clavier_pour(etape_id))


async def poser_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """L'administrateur envoie une vidéo avec, en légende, le mot de l'étape.
    Quelqu'un d'autre : rien — ce bot ne lit pas ce que les clients envoient
    (il n'a pas de cerveau, seulement un parcours)."""
    if not est_admin(update):
        return
    chat_id = update.effective_chat.id
    message = update.effective_message
    video = getattr(message, "video", None)
    document = getattr(message, "document", None)
    if video is not None:
        file_id, genre, nom = video.file_id, "video", getattr(video, "file_name", "") or ""
    elif document is not None and (getattr(document, "mime_type", "") or "").startswith("video/"):
        file_id, genre, nom = document.file_id, "document", getattr(document, "file_name", "") or ""
    else:
        await dire(ctx, chat_id, contenu.VIDEO_PAS_UNE_VIDEO)
        return
    etape = parcours.etape_pour_video(getattr(message, "caption", None))
    if etape is None:
        liste = "\n".join(f"• {e['id']} — {e['titre']}" for e in contenu.ETAPES)
        await dire(ctx, chat_id, contenu.VIDEO_ETAPE_INCONNUE.replace("{liste}", liste))
        return
    parcours.enregistrer_video(etape["id"], file_id, genre, nom)
    await dire(ctx, chat_id, contenu.VIDEO_ENREGISTREE
               .replace("{titre}", etape["titre"]).replace("{etape}", etape["id"]))


async def etat_videos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/videos — l'administrateur voit ce qui est posé, étape par étape."""
    if not est_admin(update):
        return
    lignes = "\n".join(f"{'✔' if posee else '—'} {etape_id} — {titre}"
                       for etape_id, titre, posee in parcours.videos_etat())
    await dire(ctx, update.effective_chat.id, contenu.VIDEOS_ETAT.replace("{lignes}", lignes))


async def recommencer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    with parcours.connexion() as cx:
        cx.execute("DELETE FROM progression WHERE personne = ?",
                   (str(update.effective_user.id),))
        cx.commit()
    await demarrer(update, ctx)


def main() -> int:
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
    manques = parcours.config_incomplete()
    if manques and not MODE_TEST:
        # Aucun mode dégradé silencieux (SOP-01, 2026-09-16) : plutôt ne pas
        # démarrer que servir un lien mort à un vrai client.
        log.error("Configuration incomplète : %s", ", ".join(manques))
        parcours.tracer("bot-echec", "config incomplète : " + ", ".join(manques))
        return 1
    if manques:
        log.warning("MODE_TEST — manquent encore : %s", ", ".join(manques))
        parcours.tracer("bot-test", "démarrage en mode test")

    nom = os.environ.get("BOT_NOM", "?")
    if not os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "").strip():
        log.warning("TELEGRAM_ADMIN_CHAT_ID absent — les demandes de bonus seront seulement tracées")
    log.info("Bot d'accompagnement [%s] en écoute%s", nom, " (MODE_TEST)" if MODE_TEST else "")
    # pas d'appairage TOFU : ce bot sert des inconnus, /start est le parcours lui-même
    return labo_bot.demarrer(
        "bot-stake", "TELEGRAM_BOT_TOKEN",
        [CommandHandler("start", demarrer), CommandHandler("aide", aide),
         CommandHandler("recommencer", recommencer), CommandHandler("videos", etat_videos),
         MessageHandler(filters.VIDEO | filters.Document.ALL, poser_video),
         CallbackQueryHandler(bouton)],
        contenu.PANNE, tracer=parcours.tracer, log=log, allowed_updates=None,
        post_init=lambda app: _tracer_demarrage(nom))


async def _tracer_demarrage(nom):
    parcours.tracer("bot-demarrage", f"{nom} · " + ("mode test" if MODE_TEST else "réel"))


if __name__ == "__main__":
    raise SystemExit(main())
