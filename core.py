from vk_api.utils import get_random_id


class VKtools:
    def __init__(self, vk, session):
        self.vk = vk
        self.session = session

    def search(self, user):
        print(user)
        print(user.search_city)
        print(user.search_age_from)
        print(user.search_age_to)
        req = self.session.users.search(
            count=1000,
            fields=['photo_id', 'sex', 'bdate', 'city'],
            hometown=user.search_city,
            sex=user.search_sex,
            age_from=user.search_age_from,
            age_to=user.search_age_to,
            status=user.search_status,
            has_photo=1,
            is_closed=False,
            can_access_closed=True
        )
        try:
            users = req['items']
        except KeyError:
            return None

        return users

    def photos(self, owner_id):
        photos = self.session.photos.get(
            owner_id=owner_id,
            album_id='profile',
            extended=1,
        )
        try:
            photos = photos['items']
        except KeyError:
            return None

        photos_list = sorted(photos, key=lambda k: k['likes']['count'], reverse=True)

        if len(photos_list) > 3:
            photos_list = photos_list[:3]

        result_ = list()

        for photo in photos_list:
            media_id = photo['id']
            result_.append(f'photo{owner_id}_{media_id}')

        return result_

    def simple_message(self, message_text, peer_id, keyboard=None):
        if keyboard is not None:
            self.vk.messages.send(
                peer_id=peer_id,
                random_id=get_random_id(),
                keyboard=keyboard,
                message=message_text
            )
        else:
            self.vk.messages.send(
                peer_id=peer_id,
                random_id=get_random_id(),
                message=message_text
            )
