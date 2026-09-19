"""Tests des handlers Telegram — le fichier que le contre-audit du 2026-09-17
a trouvé entièrement non testé (tous les défauts sérieux vivaient là).

On ne parle jamais à Telegram : on branche de faux objets et on vérifie ce
que le bot AURAIT envoyé. Ignorés si python-telegram-bot n'est pas installé
(le Python du Mac ne l'a pas, le conteneur oui).

Lancement : python3 -m unittest discover -s pipeline/tests
"""

import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import telegram  # noqa: F401
    TELEGRAM = True
except Exception:
    TELEGRAM = False

import parcours  # noqa: E402


class FauxBot:
    """Enregistre au lieu d'envoyer."""

    def __init__(self):
        self.envois = []

    async def send_message(self, chat_id, text, parse_mode=None, reply_markup=None):
        self.envois.append(("texte", text, reply_markup))
        self.destinataires = getattr(self, "destinataires", []) + [chat_id]

    async def send_video(self, chat_id, video, caption=None, parse_mode=None,
                         reply_markup=None):
        self.envois.append(("video", caption, reply_markup))


class FauxCtx:
    def __init__(self):
        self.bot = FauxBot()
        self.error = None


class MessageInaccessible:
    """Ce que Telegram renvoie quand le message porteur du bouton est trop
    vieux : il n'a PAS de reply_text. C'est le crash n°2 du contre-audit."""

    def __getattr__(self, nom):
        raise AttributeError(f"'InaccessibleMessage' object has no attribute '{nom}'")


class FausseRequete:
    def __init__(self, data, repondre_leve=False):
        self.data = data
        self.message = MessageInaccessible()
        self._repondre_leve = repondre_leve
        self.clavier_retire = False

    async def answer(self):
        if self._repondre_leve:
            from telegram.error import BadRequest
            raise BadRequest("Query is too old")

    async def edit_message_reply_markup(self, reply_markup=None):
        self.clavier_retire = True


class FauxUpdate:
    def __init__(self, personne="42", requete=None):
        self.callback_query = requete
        self.effective_user = type("U", (), {"id": personne, "username": "toto",
                                             "first_name": "Toto"})()
        self.effective_chat = type("C", (), {"id": 1})()
        self.effective_message = type("M", (), {})()


@unittest.skipUnless(TELEGRAM, "python-telegram-bot absent (normal sur le Mac)")
class TestHandlers(unittest.TestCase):
    def setUp(self):
        self._trace, parcours.labo_trace = parcours.labo_trace, None
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["PARCOURS_DB"] = str(Path(self._tmp.name) / "p.db")
        os.environ["STAKE_LIEN_PARRAINAGE"] = "https://exemple.test/r/sofiane"
        os.environ["VPN_NOM"] = "UnVPN"
        os.environ["VIDEOS_JSON"] = str(Path(self._tmp.name) / "videos.json")
        import bot
        self.bot = bot

    def tearDown(self):
        parcours.labo_trace = self._trace
        self._tmp.cleanup()
        for c in ("PARCOURS_DB", "STAKE_LIEN_PARRAINAGE", "VPN_NOM", "VIDEOS_JSON"):
            os.environ.pop(c, None)

    def lancer(self, coro):
        return asyncio.run(coro)

    def test_start_repond_meme_sans_message_accessible(self):
        ctx = FauxCtx()
        self.lancer(self.bot.demarrer(FauxUpdate(), ctx))
        self.assertGreaterEqual(len(ctx.bot.envois), 2)      # accueil + question de départ
        self.assertIsNotNone(ctx.bot.envois[-1][2])          # avec des boutons

    def test_partir_de_zero_sert_directement_le_vpn(self):
        ctx = FauxCtx()
        self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("depart:zero")), ctx))
        self.assertIn("Installer le VPN", ctx.bot.envois[-1][1])
        self.assertIn("UnVPN", ctx.bot.envois[-1][1])

    def test_avoir_de_la_crypto_pose_la_question_vpn_puis_sert_le_compte(self):
        ctx = FauxCtx()
        self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("depart:crypto")), ctx))
        self.assertIn("VPN", ctx.bot.envois[-1][1])
        self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("vpn:non")), ctx))
        self.assertIn("Créer ton compte", ctx.bot.envois[-1][1])

    def test_un_start_apres_la_question_de_depart_repose_la_question_vpn(self):
        ctx = FauxCtx()
        self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("depart:crypto")), ctx))
        ctx2 = FauxCtx()
        self.lancer(self.bot.demarrer(FauxUpdate(), ctx2))
        self.assertIn("VPN", ctx2.bot.envois[-1][1])
        self.assertIsNotNone(ctx2.bot.envois[-1][2])

    def test_demande_de_bonus_previent_l_admin_et_avance(self):
        os.environ["TELEGRAM_ADMIN_CHAT_ID"] = "999"
        os.environ["BOT_NOM"] = "JD"
        try:
            cx = parcours.ouvrir()
            parcours.ecrire_etat(cx, "42", vpn=False, debutant=False, etape="bonus")
            cx.close()
            ctx = FauxCtx()
            self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("bonus:demande")), ctx))
            self.assertIn(999, ctx.bot.destinataires)
            admin = [e for e, d in zip(ctx.bot.envois, ctx.bot.destinataires) if d == 999][0]
            self.assertIn("JD", admin[1]); self.assertIn("@toto", admin[1])
            self.assertIn("Tes premiers pas", ctx.bot.envois[-1][1])
        finally:
            os.environ.pop("TELEGRAM_ADMIN_CHAT_ID", None); os.environ.pop("BOT_NOM", None)

    def test_demande_de_bonus_sans_admin_ne_bloque_pas_la_personne(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, debutant=False, etape="bonus")
        cx.close()
        ctx = FauxCtx()
        self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("bonus:demande")), ctx))
        self.assertIn("Tes premiers pas", ctx.bot.envois[-1][1])
        self.assertEqual(len(parcours.demandes_bonus()), 1)

    def test_l_etape_bonus_a_son_propre_clavier(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, debutant=False, etape="bonus")
        cx.close()
        ctx = FauxCtx()
        self.lancer(self.bot.demarrer(FauxUpdate(), ctx))
        boutons = [b.callback_data for ligne in ctx.bot.envois[-1][2].inline_keyboard for b in ligne]
        self.assertIn("bonus:demande", boutons); self.assertIn("fait:bonus", boutons)

    def test_bouton_sur_message_trop_vieux_repond_quand_meme(self):
        """Le scénario phare : la personne revient 3 jours après et clique
        « C'est fait » sur le message resté à l'écran."""
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, etape="compte")
        cx.close()
        ctx = FauxCtx()
        self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("fait:compte")), ctx))
        self.assertTrue(ctx.bot.envois, "le bot n'a rien répondu")
        self.assertIn("Vérifier ton compte", ctx.bot.envois[-1][1])

    def test_query_expiree_ne_perd_pas_le_clic(self):
        """Au redémarrage du conteneur, answer() lève « query is too old » :
        le clic doit quand même faire avancer le parcours."""
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, etape="compte")
        cx.close()
        ctx = FauxCtx()
        self.lancer(self.bot.bouton(
            FauxUpdate(requete=FausseRequete("fait:compte", repondre_leve=True)), ctx))
        self.assertTrue(ctx.bot.envois)
        cx = parcours.ouvrir()
        self.assertEqual(parcours.lire_etat(cx, "42")["etape"], "verification")

    def test_vieux_bouton_le_dit_au_lieu_de_reculer(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, etape="depot")
        cx.close()
        ctx = FauxCtx()
        self.lancer(self.bot.bouton(FauxUpdate(requete=FausseRequete("fait:compte")), ctx))
        self.assertIn("déjà validée", ctx.bot.envois[-1][1])
        cx = parcours.ouvrir()
        self.assertEqual(parcours.lire_etat(cx, "42")["etape"], "depot")

    def test_aide_sur_etape_disparue_ne_plante_pas(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, etape="etape-renommee")
        cx.close()
        ctx = FauxCtx()
        self.lancer(self.bot.aide(FauxUpdate(), ctx))
        self.assertTrue(ctx.bot.envois)

    def test_reprise_donne_toujours_des_boutons(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, etape="depot")
        cx.close()
        ctx = FauxCtx()
        self.lancer(self.bot.demarrer(FauxUpdate(), ctx))
        self.assertIsNotNone(ctx.bot.envois[-1][2], "cul-de-sac muet")

    def test_un_texte_tres_long_part_en_plusieurs_messages(self):
        ctx = FauxCtx()
        self.lancer(self.bot.dire(ctx, 1, "x " * 3000))
        self.assertGreater(len(ctx.bot.envois), 1)
        for _, texte, _ in ctx.bot.envois:
            self.assertLessEqual(len(texte), 4096)

    def test_le_gras_devient_du_html_et_le_reste_est_echappe(self):
        self.assertEqual(self.bot.en_html("**a** <b>"), "<b>a</b> &lt;b&gt;")
        self.assertIn("'", self.bot.en_html("l'apostrophe"))


if __name__ == "__main__":
    unittest.main()
