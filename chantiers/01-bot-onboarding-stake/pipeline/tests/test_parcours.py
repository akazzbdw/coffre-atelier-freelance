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
        for cle in ("PARCOURS_DB", "STAKE_LIEN_PARRAINAGE", "VPN_NOM"):
            os.environ.pop(cle, None)


class TestEtapes(Base):
    def test_le_vpn_n_est_servi_qu_a_qui_le_demande(self):
        sans = [e["id"] for e in parcours.etapes_pour(False)]
        avec = [e["id"] for e in parcours.etapes_pour(True)]
        self.assertNotIn("vpn", sans)
        self.assertEqual(avec[0], "vpn")
        self.assertEqual(len(avec), len(sans) + 1)

    def test_les_quatre_etapes_du_brief_sont_la(self):
        ids = [e["id"] for e in parcours.etapes_pour(False)]
        self.assertEqual(ids, ["compte", "verification", "depot", "jeux"])

    def test_chaque_etape_a_un_texte_et_une_aide(self):
        for etape in contenu.ETAPES:
            self.assertTrue(etape["corps"].strip(), etape["id"])
            self.assertTrue(etape["aide"].strip(), etape["id"])
            self.assertGreater(etape["minutes"], 0, etape["id"])

    def test_le_lien_de_parrainage_est_dans_l_etape_compte(self):
        etapes = parcours.etapes_pour(False)
        texte = parcours.rendu(etapes[0], "https://exemple.test/r/sofiane",
                               "UnVPN", (1, 4))
        self.assertIn("https://exemple.test/r/sofiane", texte)
        self.assertIn("Étape 1/4", texte)

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
        vues = parcours.simuler(entrees=["n", "f", "f", "f", "f"],
                                sortie=lignes.append)
        self.assertEqual(vues, ["compte", "verification", "depot", "jeux"])
        self.assertIn(contenu.FIN, "\n".join(lignes))

    def test_parcours_complet_avec_vpn_et_un_blocage(self):
        lignes = []
        vues = parcours.simuler(entrees=["o", "b", "f", "f", "f", "f", "f"],
                                sortie=lignes.append)
        self.assertEqual(vues[0], "vpn")
        self.assertEqual(len(vues), 5)
        texte = "\n".join(lignes)
        self.assertIn("version gratuite", texte)   # l'aide du VPN a bien été servie
        self.assertIn(contenu.FIN, texte)

    def test_la_question_vpn_explique_avant_de_redemander(self):
        lignes = []
        parcours.simuler(entrees=["q", "n", "f", "f", "f", "f"],
                         sortie=lignes.append)
        texte = "\n".join(lignes)
        self.assertIn(contenu.AIDE_VPN.split("\n")[0], texte)


if __name__ == "__main__":
    unittest.main()
