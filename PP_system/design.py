import pygame
pygame.init()
pygame.font.init()


def color(c='white'):
    """
    > Cores no formato RGB.

    :param c: a cor literal desejada - em inglês - (ex: 'red')
    :return: cor no formato RGB.
    """

    colors = {'white': [255, 255, 255], 'red': [255, 0, 0],
              'blue': [0, 0, 255], 'yellow': [255, 255, 0],
              'green': [0, 255, 0], 'black': [0, 0, 0],
              'dark brown': [36, 21, 7], 'moss green': [12, 53, 18],
              'dark red': [108, 0, 0], 'dark green': [0, 54, 4],
              'mid yellow': [204, 204, 0], 'mid blue': [0, 73, 153]}

    for key, value in colors.items():
        if c == key:
            c = value
    return c


def display_text(txt, font, size, col, pos, screen, centralize=False, long_txt=False, space=10):

    txt_object = pygame.font.SysFont(font, size)
    line_verifier = 0

    if not long_txt:
        txt_display = txt_object.render(txt, True, color(col))

        if centralize:
            blit_pos = (pos[0] - txt_display.get_size()[0] / 2, pos[1] - txt_display.get_size()[1] / 2)
        else:
            blit_pos = pos

        screen.blit(txt_display, blit_pos)

    else:
        for txt_line in txt:
            txt_display = txt_object.render(txt_line, True, color(col))

            line_verifier += 1
            if centralize:
                blit_pos = (pos[0] - txt_display.get_size()[0] / 2, pos[1] - txt_display.get_size()[1] / 2)
            else:
                blit_pos = pos

            blit_pos = (blit_pos[0], blit_pos[1] + (txt_display.get_size()[1] * line_verifier) + space)

            screen.blit(txt_display, blit_pos)


def get_button_center(button):

    center = button['Pos'][0] + button['Size'][0] / 2, button['Pos'][1] + button['Size'][1] / 2
    return center
