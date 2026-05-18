import json
import os

from datetime import datetime

CAMPANAS_FILE = "data/campanas.json"


def load_campanas():

    if not os.path.exists(CAMPANAS_FILE):
        return []

    with open(CAMPANAS_FILE, "r") as f:
        return json.load(f)


def save_campanas(campanas):

    with open(CAMPANAS_FILE, "w") as f:

        json.dump(
            campanas,
            f,
            indent=4
        )


def registrar_campana(
    tipo,
    mensaje,
    usuarios
):

    campanas = load_campanas()

    nueva = {
        "tipo": tipo,
        "mensaje": mensaje,
        "usuarios": usuarios,
        "fecha": str(datetime.now())
    }

    campanas.append(nueva)

    save_campanas(campanas)


def ver_campanas():

    return load_campanas()