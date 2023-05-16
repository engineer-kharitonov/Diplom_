from vk_api.keyboard import VkKeyboardColor


def get_changed_preferences_keyboard(keyboard):
    keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)
    return keyboard


def get_sex_options_keyboard(keyboard):
    keyboard.add_button('Парни', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Девушки', color=VkKeyboardColor.PRIMARY)
    return keyboard


def get_search_options_keyboard(keyboard):
    keyboard.add_button('Пол', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Возраст', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Город', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Семейное положение', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)
    return keyboard


def get_search_status_options_keyboard(keyboard):
    keyboard.add_button('Не женат (Не замужем)', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Все сложно', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button('В активном поиске', color=VkKeyboardColor.PRIMARY)
    return keyboard


def get_main_activity_keyboard(keyboard):
    keyboard.add_button('Дальше', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Посмотреть страницу', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Настройки поиска', color=VkKeyboardColor.PRIMARY)
    return keyboard
