"""Le bot Telegram du chantier 01 — une PORTE, pas un cerveau.

Toutes les DÉCISIONS sont dans parcours.py (et sous tests) ; tous les TEXTES
dans contenu.py. Ici : Telegram, les boutons, et rien d'autre.

Le bot appartient à Sofiane (créé sur son compte @BotFather) ; Zakaria
n'héberge que l'exécution — garde-fou du CLAUDE.md du chantier.

Env requis : TELEGRAM_BOT_TOKEN, STAKE_LIEN_PARRAINAGE, VPN_NOM.
Env optionnel : MODE_TEST=1 (autorise le démarrage sans lien réel et montre
les emplacements vidéo), VIDEOS_JSON (chemin du fichier des vidéos).

Durci le 2026-09-17 après contre-audit (SOP-01 Phase 5). Trois règles tenues
partout dans ce fichier :
  1. on répond TOUJOURS par `ctx.bot.send_message` — jamais `query.message.reply_*`,
     qui n'existe plus quand le message porteur du bouton est trop vieux ;
  2. on ne fait jamais confiance au bouton cliqué, seulement à l'état en base ;
  3. un handler ne meurt jamais en silence — au pire il dit quelque chose.
"""

import html
import json
import logging
import os
import re
import sys
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contenu  # noqa: E402
import parcours  # noqa: E402

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.INFO)
log = logging.getLogger("bot-stake")

MODE_TEST = os.environ.get("MODE_TEST") == "1"


def videos() -> dict:
    """{id_etape: file_id Telegram} — vide tant que le monteur n'a pas livré.

    Une vidéo se dépose une fois dans Telegram, on garde son file_id ici :
    le parcours ne bouge pas, les fichiers s'ajoutent.
    """
    chemin = Path(os.environ.get("VIDEOS_JSON", "/data/videos.json"))
    if not chemin.exists():
        return {}
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except Exception as e:
        # jamais muet : un fichier de vidéos cassé se voit (contre-audit)
        log.error("videos.json illisible (%s) — parcours servi sans vidéo", e)
        parcours.tracer("bot-echec", f"videos.json illisible : {e}")
        return {}


def en_html(texte: str) -> str:
    """**gras** → <b>gras</b>, le reste échappé (pas de Markdown capricieux)."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>",
                  html.escape(texte, quote=False), flags=re.S)


def clavier_etape(etape_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(contenu.BOUTON_FAIT, callback_data=f"fait:{etape_id}"),
        InlineKeyboardButton(contenu.BOUTON_BLOQUE, callback_data=f"bloque:{etape_id}"),
    ]])


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
    morceaux = parcours.decouper(texte)
    for i, morceau in enumerate(morceaux):
        await ctx.bot.send_message(
            chat_id=chat_id, text=en_html(morceau), parse_mode=ParseMode.HTML,
            reply_markup=clavier if i == len(morceaux) - 1 else None)


async def retirer_clavier(requete) -> None:
    """Le message qu'on vient de traiter ne doit plus proposer ses boutons."""
    try:
        await requete.edit_message_reply_markup(reply_markup=None)
    except TelegramError:
        pass          # message trop vieux ou déjà édité — sans conséquence


async def envoyer_etape(ctx, chat_id: int, personne: str, etape_id: str,
                        vpn_demande: bool) -> None:
    lien, vpn_nom = parcours.config()
    etapes = parcours.etapes_pour(vpn_demande)
    etape = parcours.etape_par_id(etapes, etape_id)
    if etape is None:
        # ne peut plus arriver (etat_utilisable répare) — mais on ne se tait pas
        log.error("étape inconnue demandée : %s", etape_id)
        parcours.tracer("bot-echec", f"étape inconnue : {etape_id}")
        await dire(ctx, chat_id, contenu.DEJA_FINI)
        return
    texte = parcours.rendu(etape, lien, vpn_nom, parcours.position(etapes, etape_id))
    parcours.tracer("parcours-etape", f"{personne} · {etape_id}")
    fichier = videos().get(etape_id)
    if fichier:
        try:
            await ctx.bot.send_video(chat_id=chat_id, video=fichier,
                                     caption=en_html(texte),
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=clavier_etape(etape_id))
            return
        except TelegramError as e:
            # une vidéo qui ne part pas ne doit pas priver de l'étape
            log.error("vidéo %s refusée (%s) — étape servie en texte", etape_id, e)
            parcours.tracer("bot-echec", f"vidéo {etape_id} refusée : {e}")
    if MODE_TEST:
        texte += f"\n\n[ 🎥 emplacement vidéo prêt — {etape_id} ]"
    await dire(ctx, chat_id, texte, clavier_etape(etape_id))


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
        await envoyer_etape(ctx, chat_id, personne, etat["etape"],
                            bool(etat["vpn"]))
        return

    parcours.tracer("parcours-debut", personne)
    await dire(ctx, chat_id, contenu.ACCUEIL)
    await dire(ctx, chat_id, contenu.QUESTION_VPN, clavier_vpn())


async def bouton(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    requete = update.callback_query
    try:
        await requete.answer()
    except TelegramError:
        pass          # « query is too old » après un redémarrage : on continue
    chat_id = update.effective_chat.id
    personne = str(update.effective_user.id)
    action, _, valeur = (requete.data or "").partition(":")

    if action == "vpn":
        if valeur == "quoi":
            await dire(ctx, chat_id, contenu.AIDE_VPN, clavier_vpn(complet=False))
            return
        suite, etape = parcours.choisir_vpn(personne, valeur == "oui")
        await retirer_clavier(requete)
        if suite == "ignore":       # vieux bouton : on ne renvoie personne au début
            await dire(ctx, chat_id, contenu.DEJA_REPONDU)
            return
        await envoyer_etape(ctx, chat_id, personne, etape,
                            valeur == "oui")
        return

    if action == "bloque":
        aide = parcours.aide_courante(personne)
        if aide is None:
            await dire(ctx, chat_id, contenu.PLUS_DANS_LE_PARCOURS)
            return
        etape_id, texte = aide
        await dire(ctx, chat_id, texte, clavier_etape(etape_id))
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
            vpn = bool(parcours.lire_etat(cx, personne)["vpn"])
        await envoyer_etape(ctx, chat_id, personne, etape, vpn)


async def aide(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    aide_ = parcours.aide_courante(str(update.effective_user.id))
    if aide_ is None:
        await dire(ctx, chat_id, contenu.PLUS_DANS_LE_PARCOURS)
        return
    etape_id, texte = aide_
    await dire(ctx, chat_id, texte, clavier_etape(etape_id))


async def recommencer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    with parcours.connexion() as cx:
        cx.execute("DELETE FROM progression WHERE personne = ?",
                   (str(update.effective_user.id),))
        cx.commit()
    await demarrer(update, ctx)


async def incident(update: object, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Filet de dernier recours : aucune erreur ne laisse la personne sans
    réponse, et aucune ne reste invisible côté Labo."""
    log.exception("erreur non rattrapée", exc_info=ctx.error)
    parcours.tracer("bot-echec", f"erreur non rattrapée : {ctx.error!r}")
    chat = getattr(update, "effective_chat", None)
    if chat is not None:
        try:
            await ctx.bot.send_message(chat_id=chat.id, text=contenu.PANNE)
        except TelegramError:
            pass


def main() -> int:
    jeton = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not jeton:
        log.error("TELEGRAM_BOT_TOKEN absent — le bot ne démarre pas")
        parcours.tracer("bot-echec", "TELEGRAM_BOT_TOKEN absent")
        return 1

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

    app = Application.builder().token(jeton).build()
    app.add_handler(CommandHandler("start", demarrer))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(CommandHandler("recommencer", recommencer))
    app.add_handler(CallbackQueryHandler(bouton))
    app.add_error_handler(incident)
    log.info("Bot d'accompagnement en écoute%s", " (MODE_TEST)" if MODE_TEST else "")
    parcours.tracer("bot-demarrage", "mode test" if MODE_TEST else "réel")
    app.run_polling()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
