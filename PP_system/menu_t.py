import pygame
from PP_system import tools

pygame.init()


def get_mouse_collision(menu, button):
    """
    > Verifica se o mouse está posicionado em cima de um botão do MenuSystem.

    :param menu: O próprio objeto de classe MenuSystem.
    :param button: O rect do botão escolhido.
    :return: True se o mouse está em cima do botão; False em caso contrário.
    """

    if menu.mouse_pos[0] in range(int(button['Rect'][0][0]), int(button['Rect'][0][0] + button['Rect'][1][0] + 1)):
        if menu.mouse_pos[1] in range(int(button['Rect'][0][1]), int(button['Rect'][0][1] + button['Rect'][1][1] + 1)):

            return True

    else:

        return False


def get_all_mouse_collision(menu, buttons, collisions):

    for key, value in buttons.items():

        w_range = int(value['Rect'][0][0]), int(value['Rect'][0][0] + value['Rect'][1][0] + 1)
        h_range = int(value['Rect'][0][1]), int(value['Rect'][0][1] + value['Rect'][1][1] + 1)

        if menu.mouse_pos[0] in range(w_range[0], w_range[1]) and menu.mouse_pos[1] in range(h_range[0], h_range[1]):
            collisions[key] = True

        else:
            collisions[key] = False


def create_button(image, rect, path=''):

    path_dict = {'menu': 'paca-paua/sprites/menu/menu/', 'f-fight': 'paca-paua/sprites/menu/free-fight/',
                 'char-selection': 'paca-paua/sprites/menu/char-selection/', 'saves': 'paca-paua/sprites/menu/saves/',
                 'tutorial': 'paca-paua/sprites/menu/tutorial/'}

    if path.strip() != '':
        path = path_dict[path]
    button = dict()

    button['Sprite'] = pygame.image.load(f'{path}{image}')
    button['Sprite'] = tools.set_size(button['Sprite'], rect[1])

    button['Size'] = rect[1]
    button['Pos'] = rect[0]
    button['Rect'] = rect

    return button


def blit_buttons(screen, *buttons):

    for button in buttons:
        screen.blit(button['Sprite'], button['Pos'])
