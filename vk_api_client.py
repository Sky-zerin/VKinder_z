import vk_api
from vk_api.exceptions import ApiError


class VkApiClient:
    def __init__(self, token: str):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()

    def get_user_info(self, user_id: int) -> dict:
        """Получить данные пользователя, который общается с ботом"""
        try:
            user = self.vk.users.get(
                user_ids=user_id,
                fields="sex,bdate,city"
            )[0]
            return user
        except ApiError:
            return {}

    def search_users(
        self,
        sex: int,
        city_id: int,
        age_from: int,
        age_to: int,
        offset: int = 0,
        count: int = 10
    ) -> list:
        """Поиск пользователей ВК"""
        try:
            response = self.vk.users.search(
                sex=sex,
                city=city_id,
                age_from=age_from,
                age_to=age_to,
                has_photo=1,
                offset=offset,
                count=count
            )
            return response.get("items", [])
        except ApiError:
            return []

    def get_top_photos(self, user_id: int, count: int = 3) -> list:
        """Получить топ-фото пользователя по лайкам"""
        try:
            photos = self.vk.photos.get(
                owner_id=user_id,
                album_id="profile",
                extended=1
            )["items"]

            photos.sort(
                key=lambda x: x["likes"]["count"],
                reverse=True
            )

            top_photos = []
            for photo in photos[:count]:
                top_photos.append(
                    f"photo{photo['owner_id']}_{photo['id']}"
                )

            return top_photos
        except ApiError:
            return []
