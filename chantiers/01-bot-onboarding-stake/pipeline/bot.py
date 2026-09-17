"""Le bot Telegram du chantier 01 — une PORTE, pas un cerveau.

Toute la logique d'étapes est dans parcours.py, tous les textes dans
contenu.py. Ici : Telegram, les boutons, et rien d'autre.

Le bot appartient à Sofiane (créé sur son compte @BotFather) ; Zakaria
n'héberge que l'exécution — garde-fou du CLAUDE.md du chantier.

Env requis : TELEGRAM_BOT_TOKEN, STAKE_LIEN_PARRAINAGE, VPN_NOM.
Env optionnel : MODE_TEST=1 (autorise le démarrage sans lien réel et montre
les emplacements vidéo), VIDEOS_JSON (chemin du fichier des vidéos).
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
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except Exception:
        return {}


def en_html(texte: str) -> str:
    """**gras** → <b>gras</b>, le reste échappé (pas de Markdown capricieux)."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(texte),
                  flags=re.S)


def clavier_etape(etape_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(contenu.BOUTON_FAIT, callback_data=f"fait:{etape_id}"),
        InlineKeyboardButton(contenu.BOUTON_BLOQUE, callback_data=f"bloque:{etape_id}"),
    ]])


async def envoyer_etape(cible, personne: str, etape_id: str, vpn_demande: bool):
    lien, vpn_nom = parcours.config()
    etapes = parcours.etapes_pour(vpn_demande)
    etape = parcours.etape_par_id(etapes, etape_id)
    if etape is None:
        return
    texte = parcours.rendu(etape, lien, vpn_nom, parcours.position(etapes, etape_id))
    fichier = videos().get(etape_id)
    if fichier:
        await cible.reply_video(fichier, caption=en_html(texte),
                                parse_mode=ParseMode.HTML,
                                reply_markup=clavier_etape(etape_id))
        return
    if MODE_TEST:
        texte += f"\n\n[ 🎥 emplacement vidéo prêt — {etape_id} ]"
    await cible.reply_text(en_html(texte), parse_mode=ParseMode.HTML,
                           reply_markup=clavier_etape(etape_id))
    parcours.tracer("parcours-etape", f"{personne} · {etape_id}")


async def demarrer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    personne = str(update.effective_user.id)
    cx = parcours.ouvrir()
    etat = parcours.lire_etat(cx, personne)

    if etat["fini"]:
        await update.message.reply_text(contenu.DEJA_FINI)
        return
    if etat["etape"]:  # reprise : on rend la main exactement où il s'était arrêté
        await update.message.reply_text(contenu.RETOUR)
        await envoyer_etape(update.message, personne, etat["etape"],
                            bool(etat["vpn"]))
        parcours.tracer("parcours-reprise", personne)
        return

    parcours.ecrire_etat(cx, personne, vpn=None, etape=None, fini=False)
    parcours.tracer("parcours-debut", personne)
    await update.message.reply_text(en_html(contenu.ACCUEIL),
                                    parse_mode=ParseMode.HTML)
    await update.message.reply_text(
        en_html(contenu.QUESTION_VPN), parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(contenu.BOUTON_OUI, callback_data="vpn:oui")],
            [InlineKeyboardButton(contenu.BOUTON_NON, callback_data="vpn:non")],
            [InlineKeyboardButton(contenu.BOUTON_CEST_QUOI, callback_data="vpn:quoi")],
        ]))


async def bouton(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    requete = update.callback_query
    await requete.answer()
    personne = str(update.effective_user.id)
    cx = parcours.ouvrir()
    action, _, valeur = requete.data.partition(":")

    if action == "vpn":
        if valeur == "quoi":
            await requete.message.reply_text(
                en_html(contenu.AIDE_VPN), parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(contenu.BOUTON_OUI, callback_data="vpn:oui"),
                    InlineKeyboardButton(contenu.BOUTON_NON, callback_data="vpn:non"),
                ]]))
            return
        besoin = valeur == "oui"
        premiere = parcours.etapes_pour(besoin)[0]["id"]
        parcours.ecrire_etat(cx, personne, vpn=besoin, etape=premiere)
        await envoyer_etape(requete.message, personne, premiere, besoin)
        return

    etat = parcours.lire_etat(cx, personne)
    besoin = bool(etat["vpn"])
    etapes = parcours.etapes_pour(besoin)

    if action == "bloque":
        etape = parcours.etape_par_id(etapes, valeur)
        if etape:
            await requete.message.reply_text(
                en_html(etape["aide"]), parse_mode=ParseMode.HTML,
                reply_markup=clavier_etape(valeur))
            await requete.message.reply_text(contenu.APRES_AIDE)
            parcours.tracer("parcours-blocage", f"{personne} · {valeur}")
        return

    if action == "fait":
        suite = parcours.suivante(etapes, valeur)
        if suite is None:
            parcours.ecrire_etat(cx, personne, etape=None, fini=True)
            parcours.tracer("parcours-fin", personne)
            await requete.message.reply_text(en_html(contenu.FIN),
                                             parse_mode=ParseMode.HTML)
            return
        parcours.ecrire_etat(cx, personne, etape=suite)
        await envoyer_etape(requete.message, personne, suite, besoin)


async def aide(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    personne = str(update.effective_user.id)
    cx = parcours.ouvrir()
    etat = parcours.lire_etat(cx, personne)
    if not etat["etape"]:
        await update.message.reply_text("Tape /start pour (re)commencer le parcours.")
        return
    etape = parcours.etape_par_id(parcours.etapes_pour(bool(etat["vpn"])),
                                 etat["etape"])
    await update.message.reply_text(en_html(etape["aide"]),
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=clavier_etape(etat["etape"]))


async def recommencer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cx = parcours.ouvrir()
    cx.execute("DELETE FROM progression WHERE personne = ?",
               (str(update.effective_user.id),))
    cx.commit()
    await demarrer(update, ctx)


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
    log.info("Bot d'accompagnement en écoute%s", " (MODE_TEST)" if MODE_TEST else "")
    parcours.tracer("bot-demarrage", "mode test" if MODE_TEST else "réel")
    app.run_polling()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
