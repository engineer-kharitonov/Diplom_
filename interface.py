import os
import vk_api

import random
import keyboards

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id

from core import VKtools

from database_request import Session, User, Views, CachedUsers
from sqlalchemy.sql import exists
from dotenv import load_dotenv

load_dotenv()

db_session = Session()


def state_manager(vk, user, user_text):
    keyboard = VkKeyboard(inline=True)

    vktools = VKtools(vk, None)
    if user.state == 'search_age_from':
        if not user_text.isdigit():
            vktools.simple_message('Введено не число. Введите число', user.user_id)
        else:
            user.search_age_from = int(user_text)
            user.state = 'search_age_to'
            db_session.commit()

            vktools.simple_message('До какого возраста ищем?', user.user_id)
    elif user.state == 'search_age_to':
        if not user_text.isdigit():
            vktools.simple_message('Введено не число. Введите число', user.user_id)
        elif int(user_text) < user.search_age_from:
            vktools.simple_message('Максимальный возраст не может быть меньше минимального', user.user_id)
        else:
            user.search_age_to = int(user_text)
            vktools.simple_message('Сохранено',
                                   user.user_id, keyboards.get_changed_preferences_keyboard(keyboard).get_keyboard())

            user.state = 'default'
            db_session.commit()

    elif user.state == 'city':
        user.search_city = user_text
        db_session.commit()
        vktools.simple_message('Сохранено',
                               user.user_id, keyboards.get_changed_preferences_keyboard(keyboard).get_keyboard())
        user.state = 'default'

    elif user.state == 'search_sex':
        if user_text in ['парни', 'девушки']:
            if user_text == 'парни':
                user.search_sex = 2
            elif user_text == 'девушки':
                user.search_sex = 1

            vktools.simple_message('Сохранено',
                                   user.user_id, keyboards.get_changed_preferences_keyboard(keyboard).get_keyboard())

            user.state = 'default'
            db_session.commit()
        else:
            vktools.simple_message('Выбери один из вариантов',
                                   user.user_id, keyboards.get_sex_options_keyboard(keyboard).get_keyboard())
    elif user.state == 'search_status':
        if user_text in ['не женат (не замужем)', 'все сложно', 'в активном поиске']:
            if user_text == 'не женат (не замужем)':
                user.search_status = 1
            elif user_text == 'все сложно':
                user.search_status = 5
            elif user_text == 'в активном поиске':
                user.search_status = 6

            vktools.simple_message('Сохранено',
                                   user.user_id, keyboards.get_changed_preferences_keyboard(keyboard).get_keyboard())

            user.state = 'default'
            db_session.commit()
        else:
            vktools.simple_message('Выбери один из вариантов',
                                   user.user_id, keyboards.get_search_status_options_keyboard(keyboard).get_keyboard())


def search_settings(vk, user, user_text):
    keyboard = VkKeyboard(inline=True)

    vktools = VKtools(vk, None)
    if user_text == 'настройки поиска':

        vktools.simple_message('Настройки поиска', user.user_id,
                               keyboards.get_search_options_keyboard(keyboard).get_keyboard())

    elif user_text == 'пол':
        user.state = 'search_sex'
        db_session.commit()
        vktools.simple_message('Кто тебя интересует', user.user_id,
                               keyboards.get_sex_options_keyboard(keyboard).get_keyboard())
    elif user_text == 'возраст':
        user.state = 'search_age_from'
        db_session.commit()

        vktools.simple_message('С какого возраста ищем?', user.user_id)

    elif user_text == 'город':
        user.state = 'city'
        db_session.commit()
        vktools.simple_message('Введите название города', user.user_id)

    elif user_text == 'cемейное положение':
        user.state = 'search_status'
        db_session.commit()
        vktools.simple_message('Семейное положение для поиска',
                               user.user_id, keyboards.get_search_status_options_keyboard(keyboard).get_keyboard())


def user_search(vk, user, session):
    finder = VKtools(vk, session)
    keyboard = VkKeyboard(inline=True)

    result = finder.search(user)
    viewed = [view.get() for view in user.user_views]
    filtered = [user for user in result if user['is_closed'] is False and user['id'] not in viewed]

    # обновляем кеш в бд (удаляем старые записи)
    db_session.query(CachedUsers).filter(CachedUsers.user_id == user.user_id).delete()
    # кешируем
    cached = []

    for to_cache in filtered:
        cached_user = CachedUsers(user.user_id)
        cached_user.own_id = to_cache['id']
        cached_user.first_name = to_cache['first_name']
        cached_user.last_name = to_cache['last_name']
        cached_user.bdate = to_cache.get('bdate')
        cached_user.city = to_cache.get('city', {}).get('title')
        cached.append(cached_user)

    # Сохраняем все объекты
    db_session.bulk_save_objects(cached)
    db_session.commit()

    var = random.choice(filtered)
    message = f"{var['first_name']} {var['last_name']}, {var['bdate']}, {var.get('city',{}).get('title')}"

    user.current_page = var['id']

    db_session.add(Views(user.user_id, var['id']))
    db_session.commit()

    vk.messages.send(
        peer_id=user.user_id,
        random_id=get_random_id(),
        keyboard=keyboards.get_main_activity_keyboard(keyboard).get_keyboard(),
        message=message,
        attachment=finder.photos(var['id'])
    )


def cached_users(vk, user, session):
    finder = VKtools(vk, session)
    keyboard = VkKeyboard(inline=True)

    # получаем из кеша
    result = db_session.query(CachedUsers).filter(CachedUsers.user_id == user.user_id).all()
    viewed = [view.get() for view in user.user_views]
    filtered = [user for user in result if user.own_id not in viewed]

    var = random.choice(filtered)
    message = f"{var.first_name} {var.last_name}, {var.bdate}, {var.city}"

    user.current_page = var.own_id

    db_session.add(Views(user.user_id, var.own_id))
    db_session.commit()
    print(var.own_id)
    vk.messages.send(
        peer_id=user.user_id,
        random_id=get_random_id(),
        keyboard=keyboards.get_main_activity_keyboard(keyboard).get_keyboard(),
        message=message,
        attachment=finder.photos(var.own_id)
    )


def main():
    vk_session = vk_api.VkApi(token=os.getenv("access_token"))

    long_poll = VkBotLongPoll(vk_session, os.getenv("group_id"))
    vk = vk_session.get_api()

    user_session = vk_api.VkApi(token=os.getenv("user_token"))
    session = user_session.get_api()

    for event in long_poll.listen():
        print(event)
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.obj['message']
            user_id = message['from_id']
            user_text = message['text'].lower()
            user = User(user_id)

            if db_session.query(exists().where(User.user_id == user_id)).scalar():
                user = db_session.get(User, user_id)
            else:
                db_session.add(user)
                db_session.commit()

            if user.state != 'default':
                state_manager(vk, user, user_text)

            if user_text in ['start', 'старт', 'дальше', 'начать', 'поиск', 'начать поиск']:
                user_search(vk, user, session)
            elif user_text in ['настройки поиска', 'возраст', 'пол', 'семейное положение', 'город']:
                search_settings(vk, user, user_text)
            elif user_text == 'посмотреть страницу':
                vk.messages.send(
                    peer_id=user.user_id,
                    random_id=get_random_id(),
                    message=f'vk.com/id{user.current_page}'
                )


if __name__ == '__main__':
    main()
