import os
import vk_api

import random
import time

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from core import VKtools

from database_request import Session, User, Views
from sqlalchemy.sql import exists
from dotenv import load_dotenv

load_dotenv()

db_session = Session()


def state_manager(vk, user, user_text):
    keyboard = VkKeyboard(inline=True)

    if user.state == 'search_age_from':
        if not user_text.isdigit():
            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='Введено не число. Введите число'
            )
        else:
            user.search_age_from = int(user_text)
            user.state = 'search_age_to'
            db_session.commit()

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='До какого возраста ищем?'
            )
    elif user.state == 'search_age_to':
        if not user_text.isdigit():
            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='Введено не число. Введите число'
            )
        elif int(user_text) < user.search_age_from:
            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message='Максимальный возраст не может быть меньше минимального'
            )
        else:
            keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)

            user.search_age_to = int(user_text)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Сохранено'
            )

            user.state = 'default'
            db_session.commit()

    elif user.state == 'city':
        user.search_city = user_text
        db_session.commit()
        user.state = 'default'

    elif user.state == 'search_sex':
        if user_text in ['парни', 'девушки']:
            if user_text == 'парни':
                user.search_sex = 2
            elif user_text == 'девушки':
                user.search_sex = 1

            keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Сохранено'
            )

            user.state = 'default'
            db_session.commit()
        else:
            keyboard.add_button('Парни', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Девушки', color=VkKeyboardColor.PRIMARY)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Выбери один из вариантов'
            )
    elif user.state == 'search_status':
        if user_text in ['не женат (не замужем)', 'все сложно', 'в активном поиске']:
            if user_text == 'не женат (не замужем)':
                user.search_status = 1
            elif user_text == 'все сложно':
                user.search_status = 5
            elif user_text == 'в активном поиске':
                user.search_status = 6

            keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Сохранено'
            )

            user.state = 'default'
            db_session.commit()
        else:
            keyboard.add_button('Не женат (Не замужем)', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Все сложно', color=VkKeyboardColor.PRIMARY)

            keyboard.add_line()
            keyboard.add_button('В активном поиске', color=VkKeyboardColor.PRIMARY)

            vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message='Выбери один из вариантов'
            )


def search_settings(vk, user, user_text):
    keyboard = VkKeyboard(inline=True)

    if user_text == 'Настройки поиска':
        keyboard.add_button('Пол', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Возраст', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Город', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Семейное положение', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Начать поиск'
        )

    elif user_text == 'Пол':
        user.state = 'search_sex'
        db_session.commit()

        keyboard.add_button('Парни', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Девушки', color=VkKeyboardColor.PRIMARY)

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Кто тебя интересует?'
        )

    elif user_text == 'Возраст':
        user.state = 'search_age_from'
        db_session.commit()

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='С какого возраста ищем?'
        )

    elif user_text == 'Город':
        user.state = 'city'
        db_session.commit()

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='Введите название города'
        )

    elif user_text == 'Семейное положение':
        user.state = 'search_status'
        db_session.commit()

        keyboard.add_button('Не женат (Не замужем)', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Все сложно', color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('В активном поиске', color=VkKeyboardColor.PRIMARY)

        vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Семейное положение для поиска'
        )


def user_search(vk, user, session):
    finder = VKtools(vk, session)
    keyboard = VkKeyboard(inline=True)

    keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Посмотреть страницу', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)
    result = finder.search(user)
    viewed = [view.get() for view in user.user_views]
    filtered = [user for user in result if user['is_closed'] is False and user['id'] not in viewed]

    var = random.choice(filtered)
    message = f"{var['first_name']} {var['last_name']}, {var['bdate']}, {var['city']['title']}"

    user.current_page = var['id']

    db_session.add(Views(user.user_id, var['id']))
    db_session.commit()

    vk.messages.send(
        peer_id=user.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=message,
        attachment=finder.photos(var['id'])
    )


def main():
    vk_session = vk_api.VkApi(token=os.getenv("access_token"))

    long_poll = VkBotLongPoll(vk_session, os.getenv("group_id"))
    vk = vk_session.get_api()

    user_session = vk_api.VkApi(token=os.getenv("user_token"))
    session = user_session.get_api()

    while True:

        try:
            for event in long_poll.listen():

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

                    else:
                        vk.messages.send(
                            peer_id=user.user_id,
                            random_id=get_random_id(),
                            message=f'Для взаимодействия с ботом напишите старт или воспользуйтесь кнопками'
                        )

                elif event.type == VkBotEventType.MESSAGE_REPLY:
                    message = event.obj['message']
                    user_id = message['from_id']
                    user = User(user_id)

                    if db_session.query(exists().where(User.user_id == user_id)).scalar():
                        user = db_session.get(User, user_id)
                        db_session.add(user)
                        db_session.commit()
                    else:
                        db_session.add(user)
                        db_session.commit()

        except Exception as exception:
            print(exception)
            time.sleep(5)


if __name__ == '__main__':
    main()
