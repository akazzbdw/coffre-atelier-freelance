"""Moteur du parcours guidé — sans Telegram, pour qu'il soit testable et
rejouable au terminal (parité Mac : `python3 parcours.py --simuler`).

Le bot (bot.py) n'est qu'une porte : toute la logique d'étapes et de
progression vit ici. Les textes, eux, vivent dans contenu.py.
"""

import argparse
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import contenu

PROJET = "09-atelier-freelance"
CHANTIER = "01-bot-onboarding-stake"

# boîte noire (règle Labo 2026-08-12) — best-effort, ne fait jamais planter
for _p in Path(__file__).resolve().parents:
    if (_p / "00-Systeme" / "labo_trace.py").exists():
        sys.path.append(str(_p / "00-Systeme"))
        break
try:
    import labo_trace
except Exception:  # pragma: no cover - le traçage est un bonus, pas une dépendance
    labo_trace = None


def chemin_db() -> Path:
    """/data/progression.db dans le conteneur, à côté du code sur le Mac."""
    if os.environ.get("PARCOURS_DB"):
        return Path(os.environ["PARCOURS_DB"])
    if Path("/data").is_dir():
        return Path("/data/progression.db")
    return Path(__file__).resolve().parent / "progression.db"


def ouvrir(db_path: Path | None = None) -> sqlite3.Connection:
    db_path = db_path or chemin_db()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    cx = sqlite3.connect(db_path)
    cx.execute(
        "CREATE TABLE IF NOT EXISTS progression ("
        " personne TEXT PRIMARY KEY,"
        " vpn INTEGER,"          # 1 = a demandé le VPN, 0 = non, NULL = pas encore répondu
        " etape TEXT,"           # id de l'étape en cours ; NULL = parcours fini
        " fini INTEGER DEFAULT 0,"
        " maj TEXT)"
    )
    return cx


@contextmanager
def connexion():
    """Une connexion qui se referme — les handlers du bot passent par là
    (contre-audit 2026-09-17 : une connexion par clic, jamais fermée)."""
    cx = ouvrir()
    try:
        yield cx
    finally:
        cx.close()


def etapes_pour(vpn: bool) -> list[dict]:
    """Les étapes servies à cette personne — l'étape VPN n'existe que pour qui
    a dit en avoir besoin (branche optionnelle du brief)."""
    return [e for e in contenu.ETAPES if vpn or not e.get("optionnelle")]


def remplir(texte: str, lien: str, vpn: str) -> str:
    """Remplace {lien} et {vpn}, et RIEN d'autre.

    Volontairement pas `.format()` : contenu.py est relu et corrigé par le
    demandeur, qui n'est pas codeur. Une accolade tapée dans un texte
    (« appuie sur {Connect} ») faisait planter l'étape entière
    (contre-audit 2026-09-17).
    """
    return texte.replace("{lien}", lien).replace("{vpn}", vpn)


def aide_rendue(etape: dict, lien: str, vpn: str) -> str:
    """L'aide d'une étape — les placeholders y valent aussi (contre-audit)."""
    return remplir(etape["aide"], lien, vpn)


def rendu(etape: dict, lien: str, vpn: str, position: tuple[int, int]) -> str:
    """Le message complet d'une étape, prêt à envoyer."""
    numero, total = position
    corps = remplir(etape["corps"], lien, vpn)
    return (f"**Étape {numero}/{total} — {etape['titre']}**\n\n"
            f"{corps}\n\n"
            f"⏱ {etape['minutes']} minutes")


def lire_etat(cx: sqlite3.Connection, personne: str) -> dict:
    ligne = cx.execute(
        "SELECT vpn, etape, fini FROM progression WHERE personne = ?",
        (str(personne),)).fetchone()
    if not ligne:
        return {"vpn": None, "etape": None, "fini": False, "connu": False}
    return {"vpn": None if ligne[0] is None else bool(ligne[0]),
            "etape": ligne[1], "fini": bool(ligne[2]), "connu": True}


def ecrire_etat(cx: sqlite3.Connection, personne: str, *, vpn=None,
                etape="__inchange__", fini=None) -> None:
    etat = lire_etat(cx, personne)
    vpn_v = etat["vpn"] if vpn is None else vpn
    etape_v = etat["etape"] if etape == "__inchange__" else etape
    fini_v = etat["fini"] if fini is None else fini
    cx.execute(
        "INSERT INTO progression (personne, vpn, etape, fini, maj)"
        " VALUES (?, ?, ?, ?, ?)"
        " ON CONFLICT(personne) DO UPDATE SET vpn=excluded.vpn,"
        " etape=excluded.etape, fini=excluded.fini, maj=excluded.maj",
        (str(personne), None if vpn_v is None else int(vpn_v), etape_v,
         int(bool(fini_v)), datetime.now(timezone.utc).isoformat(timespec="seconds")))
    cx.commit()


def etape_par_id(etapes: list[dict], etape_id: str) -> dict | None:
    return next((e for e in etapes if e["id"] == etape_id), None)


def position(etapes: list[dict], etape_id: str) -> tuple[int, int]:
    ids = [e["id"] for e in etapes]
    return (ids.index(etape_id) + 1, len(ids))


def suivante(etapes: list[dict], etape_id: str) -> str | None:
    """L'étape d'après — None quand le parcours est terminé."""
    ids = [e["id"] for e in etapes]
    i = ids.index(etape_id)
    return ids[i + 1] if i + 1 < len(ids) else None


def tracer(genre: str, detail: str = "") -> None:
    if labo_trace:
        try:
            labo_trace.log_event(PROJET, genre, f"{CHANTIER} · {detail}".strip(" ·"))
        except Exception:
            pass


# ------------------------------------------------- décisions (testables sans Telegram)
#
# Tout ce que le bot DÉCIDE vit ici : les handlers Telegram ne font
# qu'appeler ces fonctions et envoyer le résultat. Le contre-audit du
# 2026-09-17 a montré que les défauts sérieux étaient tous dans le fichier
# non testé (bot.py) — la logique est donc redescendue ici, sous tests.

def etat_utilisable(cx, personne: str) -> dict:
    """L'état de la personne, RÉPARÉ si l'étape stockée n'existe plus.

    Un id d'étape renommé ou supprimé dans contenu.py (fichier relu par le
    demandeur) laissait la personne dans un cul-de-sac muet : le bot disait
    « Tu en étais là : » et plus rien, à chaque /start, pour toujours.
    """
    etat = lire_etat(cx, personne)
    etat["repare"] = False
    if etat["etape"] and not etape_par_id(etapes_pour(bool(etat["vpn"])), etat["etape"]):
        etat["etape"] = etapes_pour(bool(etat["vpn"]))[0]["id"]
        etat["repare"] = True
        ecrire_etat(cx, personne, etape=etat["etape"])
    return etat


def choisir_vpn(personne: str, besoin: bool) -> tuple[str, str | None]:
    """Réponse à la question du VPN. ("suite", première étape) ou ("ignore", None).

    Ignorée si la personne a déjà dépassé la question : sans ça, un clic sur
    le tout premier message (resté dans le fil) la renvoyait au début, ou
    créait un état « fini ET à l'étape 1 » impossible (contre-audit).
    """
    with connexion() as cx:
        etat = lire_etat(cx, personne)
        if etat["fini"] or etat["etape"]:
            return ("ignore", None)
        premiere = etapes_pour(besoin)[0]["id"]
        ecrire_etat(cx, personne, vpn=besoin, etape=premiere)
        return ("suite", premiere)


def avancer(personne: str, etape_cliquee: str) -> tuple[str, str | None]:
    """« C'est fait » sur une étape. ("suite", id) · ("fini", None) · ("ignore", None).

    On se fie à l'étape EN BASE, jamais au bouton cliqué : un vieux bouton
    d'un message plus haut dans le fil faisait reculer la progression de deux
    étapes, ou plantait le handler quand l'étape n'était plus dans la liste
    (contre-audit — deux scénarios prouvés, sans intervention de personne).
    """
    with connexion() as cx:
        etat = etat_utilisable(cx, personne)
        if etat["fini"] or not etat["etape"] or etape_cliquee != etat["etape"]:
            return ("ignore", None)
        etapes = etapes_pour(bool(etat["vpn"]))
        suite = suivante(etapes, etat["etape"])
        if suite is None:
            ecrire_etat(cx, personne, etape=None, fini=True)
            return ("fini", None)
        ecrire_etat(cx, personne, etape=suite)
        return ("suite", suite)


def aide_courante(personne: str) -> tuple[str, str] | None:
    """(id de l'étape, texte d'aide) pour la personne — None si hors parcours."""
    lien, vpn = config()
    with connexion() as cx:
        etat = etat_utilisable(cx, personne)
        if etat["fini"] or not etat["etape"]:
            return None
        etape = etape_par_id(etapes_pour(bool(etat["vpn"])), etat["etape"])
        if etape is None:           # ceinture : etat_utilisable a déjà réparé
            return None
        return (etat["etape"], aide_rendue(etape, lien, vpn))


def decouper(texte: str, limite: int = 3800) -> list[str]:
    """Telegram refuse au-delà de 4096 caractères — une aide un peu longue
    écrite par le demandeur partait en erreur 400 (contre-audit)."""
    if len(texte) <= limite:
        return [texte]
    morceaux, reste = [], texte
    while len(reste) > limite:
        coupe = reste.rfind("\n", 0, limite)
        if coupe < limite // 2:
            coupe = reste.rfind(" ", 0, limite)
        if coupe <= 0:
            coupe = limite
        morceaux.append(reste[:coupe].rstrip())
        reste = reste[coupe:].lstrip()
    if reste:
        morceaux.append(reste)
    return morceaux


# ------------------------------------------------------------------ config

def config() -> tuple[str, str]:
    """(lien de parrainage, nom du VPN) — depuis l'environnement."""
    return (os.environ.get("STAKE_LIEN_PARRAINAGE", contenu.LIEN_PARRAINAGE_A_DEFINIR),
            os.environ.get("VPN_NOM", contenu.VPN_A_DEFINIR))


def config_incomplete() -> list[str]:
    """Ce qui manque encore pour une mise en ligne réelle (réponses de Sofiane)."""
    lien, vpn = config()
    manques = []
    # Une variable PRÉSENTE mais vide (le .env.example livré la pose vide) ne
    # retombait pas sur le placeholder : le bot démarrait et envoyait « Ouvre
    # ce lien : » suivi de rien (contre-audit 2026-09-17).
    if (lien.strip() in ("", contenu.LIEN_PARRAINAGE_A_DEFINIR)
            or lien.strip().startswith("#")
            or not lien.strip().startswith("http")):
        manques.append("STAKE_LIEN_PARRAINAGE (lien de parrainage, doit commencer par http)")
    if vpn.strip() in ("", contenu.VPN_A_DEFINIR) or vpn.strip().startswith("#"):
        manques.append("VPN_NOM (quel VPN gratuit)")
    return manques


# --------------------------------------------------------------- simulateur

def simuler(entrees=None, sortie=print) -> list[str]:
    """Rejoue le parcours au terminal — sert à relire les textes sans Telegram
    et à prouver le parcours de bout en bout (parité Mac du chantier).

    `entrees` : réponses successives (pour les tests). None = interactif.
    Retourne la liste des ids d'étapes parcourues.
    """
    lien, vpn = config()
    file = list(entrees or [])

    def demander(invite: str) -> str:
        if file:
            rep = file.pop(0)
            sortie(f"{invite} > {rep}")
            return rep
        return input(f"{invite} > ").strip().lower()

    sortie(contenu.ACCUEIL + "\n")
    sortie(contenu.QUESTION_VPN)
    rep = demander("[o]ui / [n]on / [q]u'est-ce que c'est")
    if rep.startswith("q"):
        sortie("\n" + contenu.AIDE_VPN + "\n")
        rep = demander("[o]ui / [n]on")
    besoin_vpn = rep.startswith("o")

    etapes = etapes_pour(besoin_vpn)
    vues = []
    for etape in etapes:
        sortie("\n" + "─" * 46)
        sortie(rendu(etape, lien, vpn, position(etapes, etape["id"])))
        sortie(f"[ 🎥 emplacement vidéo — {etape['id']} ]")
        vues.append(etape["id"])
        rep = demander(f"{contenu.BOUTON_FAIT} [f] / {contenu.BOUTON_BLOQUE} [b]")
        if rep.startswith("b"):
            sortie("\n" + etape["aide"])
            sortie(contenu.APRES_AIDE)
            demander(contenu.BOUTON_FAIT + " [f]")
    sortie("\n" + contenu.FIN)
    return vues


def main() -> int:
    ap = argparse.ArgumentParser(description="Parcours guidé — chantier 01")
    ap.add_argument("--simuler", action="store_true",
                    help="rejouer le parcours au terminal (parité Mac)")
    ap.add_argument("--config", action="store_true",
                    help="dire ce qui manque avant une mise en ligne réelle")
    args = ap.parse_args()

    if args.config:
        manques = config_incomplete()
        print("Configuration complète ✔" if not manques
              else "Manque encore :\n  - " + "\n  - ".join(manques))
        return 0
    if args.simuler:
        if labo_trace:
            with labo_trace.run(PROJET, "parcours-simulation"):
                simuler()
        else:
            simuler()
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
