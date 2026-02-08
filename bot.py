import random
from datetime import datetime

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import VK_GROUP_TOKEN, VK_USER_TOKEN
from vk_api_client import VkApiClient
from favorites import add_to_favorites, get_favorites


# --- VK INIT ---
vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

vk_user = VkApiClient(VK_USER_TOKEN)

# --- MEMORY ---
search_results = {}
search_offsets = {}


# --- UTILS ---
def send_message(user_id: int, text: str, attachments: str | None = None) -> None:
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 10**9),
        attachment=attachments
    )


# --- LOGIC ---
def show_user(user_id: int, profile: dict) -> None:
    profile_id = profile.get("id")
    if not isinstance(profile_id, int):
        return

    photos = vk_user.get_top_photos(profile_id)

    message = (
        f"{profile.get('first_name', '')} {profile.get('last_name', '')}\n"
        f"https://vk.com/id{profile_id}"
    )

    send_message(user_id, message, ",".join(photos))


def handle_search(user_id: int) -> None:
    user_info = vk_user.get_user_info(user_id)

    if not isinstance(user_info, dict) or not user_info:
        send_message(user_id, "Не удалось получить данные профиля 😢")
        return

    # --- ЯВНАЯ ПРОВЕРКА ДАННЫХ ---
    if "sex" not in user_info or user_info["sex"] not in (1, 2):
        send_message(user_id, "Укажи пол в профиле VK и попробуй снова 🙂")
        return

    if "city" not in user_info or not user_info["city"]:
        send_message(user_id, "Укажи город в профиле VK и попробуй снова 🙂")
        return

    if "bdate" not in user_info:
        send_message(user_id, "Укажи дату рождения в профиле VK и попробуй снова 🙂")
        return

    sex = user_info["sex"]
    city = user_info["city"]
    bdate = user_info["bdate"]

    # город может быть dict или int
    if isinstance(city, dict):
        city_id = city.get("id")
    else:
        city_id = city

    if not city_id:
        send_message(user_id, "Не удалось определить город 😕")
        return

    parts = bdate.split(".")
    if len(parts) != 3:
        send_message(user_id, "Дата рождения должна быть указана с годом 😕")
        return

    birth_year = int(parts[2])
    age = datetime.now().year - birth_year

    target_sex = 1 if sex == 2 else 2

    results = vk_user.search_users(
        sex=target_sex,
        city_id=city_id,
        age_from=age - 2,
        age_to=age + 2
    )

    if not results:
        send_message(user_id, "Никого не найдено 😔")
        return

    search_results[user_id] = results
    search_offsets[user_id] = 0

    show_user(user_id, results[0])



def handle_next(user_id: int) -> None:
    results = search_results.get(user_id)

    if not results:
        send_message(user_id, "Сначала напиши «поиск» 🔍")
        return

    search_offsets[user_id] += 1
    offset = search_offsets[user_id]

    if offset >= len(results):
        send_message(user_id, "Анкеты закончились 😅")
        return

    show_user(user_id, results[offset])


def handle_add_favorite(user_id: int) -> None:
    results = search_results.get(user_id)
    if not results:
        send_message(user_id, "Нет анкеты для добавления ❌")
        return

    offset = search_offsets.get(user_id, 0)
    profile = results[offset]

    add_to_favorites({
        "id": profile.get("id"),
        "name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
        "profile_url": f"https://vk.com/id{profile.get('id')}",
        "added_at": datetime.now().isoformat()
    })

    send_message(user_id, "Добавлено в избранное ⭐")


def handle_show_favorites(user_id: int) -> None:
    favorites = get_favorites()

    if not favorites:
        send_message(user_id, "Список избранных пуст 📭")
        return

    text = "⭐ Избранные:\n\n"
    for fav in favorites:
        text += f"{fav['name']} — {fav['profile_url']}\n"

    send_message(user_id, text)


# --- MAIN ---
def main() -> None:
    print("BOT STARTED (NO PROFILE CHECK)")

    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue

        user_id = event.user_id
        text = event.text.lower().strip()

        try:
            if text == "поиск":
                handle_search(user_id)
            elif text == "дальше":
                handle_next(user_id)
            elif text == "в избранное":
                handle_add_favorite(user_id)
            elif text == "избранные":
                handle_show_favorites(user_id)
            else:
                send_message(
                    user_id,
                    "Команды:\n"
                    "поиск 🔍\n"
                    "дальше ➡\n"
                    "в избранное ⭐\n"
                    "избранные 📂"
                )
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
