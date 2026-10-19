"""Tests du parcours guidé — chantier 01.

Lancement : python3 -m unittest discover -s pipeline/tests
Les tests ne touchent JAMAIS le vrai registre de la boîte noire
(labo_trace neutralisé, leçon du 2026-08-15) ni la vraie base.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import contenu  # noqa: E402
import parcours  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self._trace, parcours.labo_trace = parcours.labo_trace, None
        self._tmp = tempfile.TemporaryDirectory()
        self.db = Path(self._tmp.name) / "progression.db"
        os.environ["PARCOURS_DB"] = str(self.db)
        os.environ["STAKE_LIEN_PARRAINAGE"] = "https://exemple.test/r/sofiane"
        os.environ["VPN_NOM"] = "UnVPN"

    def tearDown(self):
        parcours.labo_trace = self._trace
        self._tmp.cleanup()
        for cle in ("PARCOURS_DB", "STAKE_LIEN_PARRAINAGE", "VPN_NOM", "VIDEOS_JSON"):
            os.environ.pop(cle, None)


class TestAucunNomDansLesTextes(Base):
    def test_aucun_texte_client_ne_nomme_le_demandeur(self):
        """Demande de Zakaria (2026-10-19) : le nom de Sofiane n'apparaît jamais côté client."""
        textes = [v for k, v in vars(contenu).items() if k.isupper() and isinstance(v, str)]
        for e in contenu.ETAPES:
            textes += [e["titre"], e["corps"], e["aide"]]
        for texte in textes:
            self.assertNotIn("sofiane", texte.lower(), texte[:80])


class TestVideos(Base):
    """Les vidéos (2026-10-19) : une par étape, posées par l'administrateur."""

    def setUp(self):
        super().setUp()
        os.environ["VIDEOS_JSON"] = str(Path(self._tmp.name) / "videos.json")

    def test_la_legende_designe_une_etape_sans_deviner(self):
        self.assertEqual(parcours.etape_pour_video(" /Vérification ")["id"], "verification")
        self.assertEqual(parcours.etape_pour_video("COMPTE")["id"], "compte")
        for mauvaise in ("", None, "la deuxième", "compte verification", "video"):
            self.assertIsNone(parcours.etape_pour_video(mauvaise), mauvaise)

    def test_poser_puis_remplacer(self):
        parcours.enregistrer_video("vpn", "FID-1", "video", "v1.mp4")
        self.assertEqual(parcours.video_pour(parcours.videos_lire(), "vpn"), ("FID-1", "video"))
        parcours.enregistrer_video("vpn", "FID-2", "document", "v2.mp4")
        self.assertEqual(parcours.video_pour(parcours.videos_lire(), "vpn"), ("FID-2", "document"))
        self.assertIsNone(parcours.video_pour(parcours.videos_lire(), "compte"))
        self.assertFalse(parcours.chemin_videos().with_suffix(".json.tmp").exists(), "écriture atomique")

    def test_une_etape_inconnue_est_refusee(self):
        with self.assertRaises(ValueError):
            parcours.enregistrer_video("ailleurs", "FID", "video")
        self.assertEqual(parcours.videos_lire(), {})

    def test_l_ancienne_forme_une_chaine_est_toujours_lue(self):
        parcours.chemin_videos().write_text('{"compte": "FID-ancien"}', encoding="utf-8")
        self.assertEqual(parcours.video_pour(parcours.videos_lire(), "compte"), ("FID-ancien", "video"))

    def test_un_fichier_casse_sert_le_parcours_sans_video(self):
        parcours.chemin_videos().write_text("{pas du json", encoding="utf-8")
        self.assertEqual(parcours.videos_lire(), {})

    def test_l_etat_couvre_toutes_les_etapes_dans_l_ordre(self):
        parcours.enregistrer_video("depot", "FID", "video")
        etat = parcours.videos_etat()
        self.assertEqual([e[0] for e in etat], ["vpn", "compte", "verification", "crypto", "depot", "bonus", "jeux"])
        self.assertEqual([e[0] for e in etat if e[2]], ["depot"])

    def test_l_etape_vpn_dit_hong_kong(self):
        """La vidéo du monteur (30/09) choisit Hong Kong ; le texte dit la même chose."""
        etapes = parcours.etapes_pour(True)
        self.assertIn("Hong Kong", parcours.rendu(etapes[0], "https://x", "UnVPN", (1, 6)))


class TestEtapes(Base):
    def test_le_vpn_n_est_servi_qu_a_qui_le_demande(self):
        sans = [e["id"] for e in parcours.etapes_pour(False)]
        avec = [e["id"] for e in parcours.etapes_pour(True)]
        self.assertNotIn("vpn", sans)
        self.assertEqual(avec[0], "vpn")
        self.assertEqual(len(avec), len(sans) + 1)

    def test_la_route_courte_a_les_etapes_du_brief_plus_le_bonus(self):
        ids = [e["id"] for e in parcours.etapes_pour(False)]
        self.assertEqual(ids, ["compte", "verification", "depot", "bonus", "jeux"])

    def test_la_route_debutant_ajoute_vpn_et_crypto(self):
        """Appel Sofiane du 2026-09-19 : qui part de zéro crée le compte,
        installe le VPN, achète de la crypto, dépose."""
        ids = [e["id"] for e in parcours.etapes_pour(True, True)]
        self.assertEqual(ids, ["vpn", "compte", "verification", "crypto", "depot", "bonus", "jeux"])
        self.assertNotIn("crypto", [e["id"] for e in parcours.etapes_pour(True, False)])

    def test_chaque_etape_a_un_texte_et_une_aide(self):
        for etape in contenu.ETAPES:
            self.assertTrue(etape["corps"].strip(), etape["id"])
            self.assertTrue(etape["aide"].strip(), etape["id"])
            self.assertGreater(etape["minutes"], 0, etape["id"])

    def test_le_lien_de_parrainage_est_dans_l_etape_compte(self):
        etapes = parcours.etapes_pour(False)
        texte = parcours.rendu(etapes[0], "https://exemple.test/r/sofiane",
                               "UnVPN", parcours.position(etapes, "compte"))
        self.assertIn("https://exemple.test/r/sofiane", texte)
        self.assertIn("Étape 1/5", texte)

    def test_aucun_placeholder_ne_fuit_dans_un_rendu(self):
        lien, vpn = parcours.config()
        for etape in contenu.ETAPES:
            texte = parcours.rendu(etape, lien, vpn, (1, 5))
            self.assertNotIn("{lien}", texte)
            self.assertNotIn("{vpn}", texte)

    def test_suivante_puis_fin(self):
        etapes = parcours.etapes_pour(False)
        self.assertEqual(parcours.suivante(etapes, "compte"), "verification")
        self.assertIsNone(parcours.suivante(etapes, "jeux"))


class TestProgression(Base):
    def test_on_reprend_ou_on_s_est_arrete(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, etape="verification")
        cx.close()
        cx2 = parcours.ouvrir()          # comme si la personne revenait 3 jours après
        etat = parcours.lire_etat(cx2, "42")
        self.assertEqual(etat["etape"], "verification")
        self.assertFalse(etat["fini"])
        self.assertTrue(etat["connu"])

    def test_deux_personnes_ne_se_marchent_pas_dessus(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "1", vpn=True, etape="vpn")
        parcours.ecrire_etat(cx, "2", vpn=False, etape="depot")
        self.assertEqual(parcours.lire_etat(cx, "1")["etape"], "vpn")
        self.assertEqual(parcours.lire_etat(cx, "2")["etape"], "depot")
        self.assertTrue(parcours.lire_etat(cx, "1")["vpn"])

    def test_inconnu_part_de_zero(self):
        cx = parcours.ouvrir()
        etat = parcours.lire_etat(cx, "999")
        self.assertFalse(etat["connu"])
        self.assertIsNone(etat["etape"])

    def test_ecrire_ne_perd_pas_le_choix_vpn(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "7", vpn=True, etape="vpn")
        parcours.ecrire_etat(cx, "7", etape="compte")   # avance sans repréciser le vpn
        self.assertTrue(parcours.lire_etat(cx, "7")["vpn"])


class TestConfig(Base):
    def test_config_complete_quand_tout_est_renseigne(self):
        self.assertEqual(parcours.config_incomplete(), [])

    def test_config_incomplete_nomme_ce_qui_manque(self):
        os.environ.pop("STAKE_LIEN_PARRAINAGE")
        manques = parcours.config_incomplete()
        self.assertEqual(len(manques), 1)
        self.assertIn("parrainage", manques[0])


class TestSimulateur(Base):
    def test_parcours_complet_sans_vpn(self):
        lignes = []
        vues = parcours.simuler(entrees=["c", "n", "f", "f", "f", "f", "f"],
                                sortie=lignes.append)
        self.assertEqual(vues, ["compte", "verification", "depot", "bonus", "jeux"])
        self.assertIn(contenu.FIN, "\n".join(lignes))

    def test_parcours_complet_avec_vpn_et_un_blocage(self):
        lignes = []
        vues = parcours.simuler(entrees=["c", "o", "b", "f", "f", "f", "f", "f", "f"],
                                sortie=lignes.append)
        self.assertEqual(vues[0], "vpn")
        self.assertEqual(len(vues), 6)
        texte = "\n".join(lignes)
        self.assertIn("version gratuite", texte)   # l'aide du VPN a bien été servie
        self.assertIn(contenu.FIN, texte)

    def test_la_question_vpn_explique_avant_de_redemander(self):
        lignes = []
        parcours.simuler(entrees=["c", "q", "n", "f", "f", "f", "f", "f"],
                         sortie=lignes.append)
        texte = "\n".join(lignes)
        self.assertIn(contenu.AIDE_VPN.split("\n")[0], texte)


    def test_parcours_debutant_avec_demande_de_bonus(self):
        lignes = []
        vues = parcours.simuler(entrees=["z", "f", "f", "f", "f", "f", "d", "f"],
                                sortie=lignes.append)
        self.assertEqual(vues, ["vpn", "compte", "verification", "crypto", "depot", "bonus", "jeux"])
        self.assertIn(contenu.BONUS_DEMANDE_OK, "\n".join(lignes))


class TestRoutes(Base):
    """V1.1 — la question de départ et l'étape bonus, sous tests comme le reste."""

    def test_partir_de_zero_donne_la_route_complete_sans_question_vpn(self):
        self.assertEqual(parcours.choisir_depart("42", True), ("suite", "vpn"))
        cx = parcours.ouvrir()
        etat = parcours.lire_etat(cx, "42")
        self.assertTrue(etat["debutant"]); self.assertTrue(etat["vpn"])

    def test_avoir_deja_de_la_crypto_passe_par_la_question_vpn(self):
        self.assertEqual(parcours.choisir_depart("42", False), ("vpn", None))
        self.assertEqual(parcours.choisir_vpn("42", False), ("suite", "compte"))

    def test_la_question_vpn_est_ignoree_avant_la_question_de_depart(self):
        self.assertEqual(parcours.choisir_vpn("42", True), ("ignore", None))

    def test_reclic_sur_la_question_de_depart_ne_change_rien(self):
        parcours.choisir_depart("42", False)
        self.assertEqual(parcours.choisir_depart("42", True), ("ignore", None))
        cx = parcours.ouvrir()
        self.assertFalse(parcours.lire_etat(cx, "42")["debutant"])

    def test_demander_le_bonus_enregistre_et_avance(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, debutant=False, etape="bonus")
        cx.close()
        self.assertEqual(parcours.demander_bonus("42", "@toto"), ("nouvelle", "jeux"))
        self.assertEqual([d[1] for d in parcours.demandes_bonus()], ["@toto"])
        cx = parcours.ouvrir()
        self.assertEqual(parcours.lire_etat(cx, "42")["etape"], "jeux")

    def test_demande_de_bonus_hors_etape_est_ignoree(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, debutant=False, etape="compte")
        cx.close()
        self.assertEqual(parcours.demander_bonus("42"), ("ignore", None))
        self.assertEqual(parcours.demandes_bonus(), [])

    def test_une_seule_demande_par_personne(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", vpn=False, debutant=False, etape="bonus")
        cx.close()
        parcours.demander_bonus("42", "@toto")
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "42", etape="bonus")      # revenu sur l'étape (recommencer)
        cx.close()
        self.assertEqual(parcours.demander_bonus("42", "@toto"), ("deja", None))
        self.assertEqual(len(parcours.demandes_bonus()), 1)

    def test_une_base_de_la_v1_recoit_la_colonne_debutant(self):
        import sqlite3
        cx = sqlite3.connect(self.db)
        cx.execute("CREATE TABLE progression (personne TEXT PRIMARY KEY, vpn INTEGER,"
                   " etape TEXT, fini INTEGER DEFAULT 0, maj TEXT)")
        cx.execute("INSERT INTO progression VALUES ('7', 0, 'depot', 0, 'x')")
        cx.commit(); cx.close()
        cx = parcours.ouvrir()
        etat = parcours.lire_etat(cx, "7")
        self.assertEqual(etat["etape"], "depot"); self.assertIsNone(etat["debutant"])


if __name__ == "__main__":
    unittest.main()


class TestVieuxBoutons(Base):
    """Les scénarios prouvés par le contre-audit du 2026-09-17 : tout ce qui
    se passe quand quelqu'un reclique un bouton resté plus haut dans le fil."""

    def test_un_vieux_bouton_ne_fait_pas_reculer(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "1", vpn=False, etape="depot")
        cx.close()
        suite, etape = parcours.avancer("1", "compte")   # vieux bouton de l'étape 1
        self.assertEqual(suite, "ignore")
        self.assertIsNone(etape)
        cx = parcours.ouvrir()
        self.assertEqual(parcours.lire_etat(cx, "1")["etape"], "depot")

    def test_reclic_sur_la_question_vpn_ne_renvoie_pas_au_debut(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "2", vpn=False, etape="jeux")
        cx.close()
        suite, _ = parcours.choisir_vpn("2", True)
        self.assertEqual(suite, "ignore")
        cx = parcours.ouvrir()
        self.assertEqual(parcours.lire_etat(cx, "2")["etape"], "jeux")

    def test_une_personne_finie_ne_repart_pas_a_l_etape_1(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "3", vpn=False, etape=None, fini=True)
        cx.close()
        self.assertEqual(parcours.choisir_vpn("3", True)[0], "ignore")
        self.assertEqual(parcours.avancer("3", "jeux")[0], "ignore")
        cx = parcours.ouvrir()
        etat = parcours.lire_etat(cx, "3")
        self.assertTrue(etat["fini"])
        self.assertIsNone(etat["etape"])   # jamais « fini ET à l'étape vpn »

    def test_clic_sur_une_etape_qui_n_existe_plus_ne_plante_pas(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "4", vpn=True, etape="vpn")
        parcours.ecrire_etat(cx, "4", vpn=False)   # elle a changé d'avis ailleurs
        cx.close()
        suite, _ = parcours.avancer("4", "vpn")    # l'étape vpn n'est plus servie
        self.assertEqual(suite, "ignore")          # au lieu d'un ValueError

    def test_avancer_normalement_marche_toujours(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "5", vpn=False, etape="compte")
        cx.close()
        self.assertEqual(parcours.avancer("5", "compte"), ("suite", "verification"))

    def test_derniere_etape_termine_le_parcours(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "6", vpn=False, etape="jeux")
        cx.close()
        self.assertEqual(parcours.avancer("6", "jeux"), ("fini", None))
        cx = parcours.ouvrir()
        self.assertTrue(parcours.lire_etat(cx, "6")["fini"])


class TestEtatRepare(Base):
    def test_une_etape_disparue_est_reparee_au_lieu_du_cul_de_sac(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "7", vpn=False, etape="etape-renommee-par-sofiane")
        etat = parcours.etat_utilisable(cx, "7")
        self.assertTrue(etat["repare"])
        self.assertEqual(etat["etape"], "compte")

    def test_aide_courante_ne_plante_jamais(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "8", vpn=False, etape="etape-qui-n-existe-plus")
        cx.close()
        etape_id, texte = parcours.aide_courante("8")
        self.assertEqual(etape_id, "compte")
        self.assertTrue(texte.strip())

    def test_aide_courante_est_none_hors_parcours(self):
        cx = parcours.ouvrir()
        parcours.ecrire_etat(cx, "9", vpn=False, etape=None, fini=True)
        cx.close()
        self.assertIsNone(parcours.aide_courante("9"))


class TestContenuRelu(Base):
    """contenu.py est relu et corrigé par le demandeur, qui n'est pas codeur :
    ses fautes de frappe ne doivent pas casser le bot (contre-audit 2026-09-17)."""

    def test_une_accolade_tapee_dans_un_texte_ne_casse_rien(self):
        texte = parcours.remplir("appuie sur {Connect} puis ouvre {lien}",
                                 "https://x.test", "UnVPN")
        self.assertIn("{Connect}", texte)      # laissé tel quel, pas de KeyError
        self.assertIn("https://x.test", texte)

    def test_le_lien_vaut_aussi_dans_une_aide(self):
        etape = {"aide": "Reprends depuis {lien} avec {vpn}"}
        texte = parcours.aide_rendue(etape, "https://x.test", "UnVPN")
        self.assertNotIn("{lien}", texte)
        self.assertNotIn("{vpn}", texte)

    def test_un_texte_trop_long_est_decoupe_sous_la_limite_telegram(self):
        long = ("Une ligne d'explication assez longue pour compter.\n" * 200)
        morceaux = parcours.decouper(long)
        self.assertGreater(len(morceaux), 1)
        for m in morceaux:
            self.assertLessEqual(len(m), 3800)
        sans_blancs = lambda s: "".join(s.split())
        self.assertEqual(sans_blancs("".join(morceaux)), sans_blancs(long))

    def test_un_texte_court_n_est_pas_touche(self):
        self.assertEqual(parcours.decouper("court"), ["court"])


class TestConfigDure(Base):
    """Le garde-fou « aucun mode dégradé silencieux » doit tenir même quand le
    .env est copié puis laissé vide (contre-audit : il ne tenait pas)."""

    def test_variable_vide_compte_comme_manquante(self):
        os.environ["STAKE_LIEN_PARRAINAGE"] = ""
        manques = parcours.config_incomplete()
        self.assertTrue(any("parrainage" in m for m in manques))

    def test_commentaire_laisse_dans_le_env_compte_comme_manquant(self):
        os.environ["STAKE_LIEN_PARRAINAGE"] = "# son lien de parrainage"
        self.assertTrue(any("parrainage" in m for m in parcours.config_incomplete()))

    def test_un_lien_qui_n_est_pas_une_url_est_refuse(self):
        os.environ["STAKE_LIEN_PARRAINAGE"] = "stake mon code SOF123"
        self.assertTrue(any("parrainage" in m for m in parcours.config_incomplete()))

    def test_vpn_vide_compte_comme_manquant(self):
        os.environ["VPN_NOM"] = "   "
        self.assertTrue(any("VPN_NOM" in m for m in parcours.config_incomplete()))
