import json

FILE = "data/usuarios.json"


def load_users():

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return {}


def save_users(users):
    

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def get_all_users():
    users = load_users()
    return users


def get_user_profile(users, user_id):

    user_id = str(user_id)

    if user_id not in users:

        users[user_id] = {
            "nombre": "",
            "objetivo": "",
            "productos": [],
            "historial": []
        }

    return users[user_id]