import json
import os
from datetime import datetime

FILENAME = "favorites.json"


def load_favorites() -> list:
    if not os.path.exists(FILENAME):
        return []

    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, ValueError):
        return []

    if not isinstance(data, list):
        return []

    return data




def save_favorites(data: list) -> None:
    with open(FILENAME, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def add_to_favorites(user_data: dict) -> None:
    favorites = load_favorites()

    user_data["added_at"] = datetime.now().isoformat()
    favorites.append(user_data)

    save_favorites(favorites)


def get_favorites() -> list:
    data = load_favorites()
    return data if isinstance(data, list) else []

