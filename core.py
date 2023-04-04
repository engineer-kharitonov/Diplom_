import random


class VKtools:
    def __init__(self, vk, session):
        self.vk = vk
        self.session = session

    def search(self, user):
        print(user)
        print(user.search_city)
        print(user.search_age_from)
        print(user.search_age_to)
        return self.session.users.search(
            count=100,
            offset=random.randrange(0, 100),
            fields=['photo_id', 'sex', 'bdate', 'city'],
            hometown=user.search_city,
            sex=user.search_sex,
            age_from=user.search_age_from,
            age_to=user.search_age_to,
            status=user.search_status,
            has_photo=1,
            is_closed=False,
            can_access_closed=True
        )['items']

    def photos(self, owner_id):
        photos = self.session.photos.get(
            owner_id=owner_id,
            album_id='profile',
            extended=1,
        )

        photos_list = sorted(photos['items'], key=lambda k: k['likes']['count'], reverse=True)

        if len(photos_list) > 3:
            photos_list = photos_list[:3]

        result_ = list()

        for photo in photos_list:
            media_id = photo['id']
            result_.append(f'photo{owner_id}_{media_id}')

        return result_
