"""Moteur du parcours guidé — sans Telegram, pour qu'il soit testable et
rejouable au terminal (parité Mac : `python3 parcours.py --simuler`).

Le bot (bot.py) n'est qu'une porte : toute la logique d'étapes et de
progression vit ici. Les textes, eux, vivent dans contenu.py.
"""

import argparse
import os
import sqlite3
import sys
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
    cx.commit()
    return cx


def etapes_pour(vpn: bool) -> list[dict]:
    """Les étapes servies à cette personne — l'étape VPN n'existe que pour qui
    a dit en avoir besoin (branche optionnelle du brief)."""
    return [e for e in contenu.ETAPES if vpn or not e.get("optionnelle")]


def rendu(etape: dict, lien: str, vpn: str, position: tuple[int, int]) -> str:
    """Le message complet d'une étape, prêt à envoyer."""
    numero, total = position
    corps = etape["corps"].format(lien=lien, vpn=vpn)
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


# ------------------------------------------------------------------ config

def config() -> tuple[str, str]:
    """(lien de parrainage, nom du VPN) — depuis l'environnement."""
    return (os.environ.get("STAKE_LIEN_PARRAINAGE", contenu.LIEN_PARRAINAGE_A_DEFINIR),
            os.environ.get("VPN_NOM", contenu.VPN_A_DEFINIR))


def config_incomplete() -> list[str]:
    """Ce qui manque encore pour une mise en ligne réelle (réponses de Sofiane)."""
    lien, vpn = config()
    manques = []
    if lien == contenu.LIEN_PARRAINAGE_A_DEFINIR:
        manques.append("STAKE_LIEN_PARRAINAGE (lien de parrainage)")
    if vpn == contenu.VPN_A_DEFINIR:
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
