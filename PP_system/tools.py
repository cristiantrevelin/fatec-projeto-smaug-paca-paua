import pygame

pygame.init()
pygame.font.init()


def get_hit_box_coords(obj, inverse=False):
    """
    > Encontra as coordenadas X e Y da hitbox do objeto.

    :param obj: O objeto que contenha um rect de movimento.
    :param inverse: True para analisar a hitbox da imagem invertida.
    :return: Uma tupla contendo as coordenadas.
    """

    if inverse:
        obj.image = pygame.transform.flip(obj.image, True, False)

    hit_box = obj.image.get_bounding_rect()

    hit_box_x = hit_box[0]
    hit_box_y = hit_box[1]
    hit_box_w = hit_box[2]
    hit_box_h = hit_box[3]

    return [hit_box_x, hit_box_y, hit_box_w, hit_box_h]


def set_focus(char, foe, sprite_iterables):
    """
    > Compara o ponto X do rect de um objeto de classe 'Character', com a posição X de outro objeto.
    > Inverte todos os sprites de uma lista global de sprites do objeto Char, para que este foque
    sempre o outro objeto.

    :param char: Objeto de classe 'Character'.
    :param foe: Objeto a ser focado sempre pelo char.
    :param sprite_iterables: Lista contendo listas de todos os sprites do char.
    :return: Nada.
    """

    if not char.is_attacking and not foe.is_attacking and not char.is_dashing:
        if foe.real_rect[0] + (foe.char_box[2] / 2) > char.real_rect[0] + (char.char_box[2] / 2):
            char.look_right = True

        elif foe.real_rect[0] + (foe.char_box[2] / 2) < char.real_rect[0] + (char.char_box[2] / 2):
            char.look_right = False

        if char.look_right and not char.current_looking_right:
            for iterable in sprite_iterables:
                for index, sprite in enumerate(iterable):
                    iterable[index] = pygame.transform.flip(sprite, True, False)

            char.current_looking_right = True

        elif not char.look_right and char.current_looking_right:
            for iterable in sprite_iterables:
                for index, sprite in enumerate(iterable):
                    iterable[index] = pygame.transform.flip(sprite, True, False)

            char.current_looking_right = False


def set_size(image, size):
    """
    > Altera as dimensões de uma imagem (ou conjunto de imagens) para as dimensões desejadas.

    :param image: Imagem, conjunto de imagens ou um conjunto contendo conjuntos de imagens.
    :param size: Iterável contendo o novo tamanho.
    :return: Nada, se "image" é um conjunto; Retorna a nova imagem, se "image" não for um conjunto.
    """

    try:
        for s_list in image:
            for index, sprite in enumerate(s_list):
                s_list[index] = pygame.transform.scale(sprite, (size[0], size[1])).convert_alpha()

    except (IndexError, TypeError):
        try:
            for index, sprite in enumerate(image):
                image[index] = pygame.transform.scale(sprite, (size[0], size[1])).convert_alpha()

        except (IndexError, TypeError):
            image = pygame.transform.scale(image, (size[0], size[1])).convert_alpha()
            return image.convert_alpha(image)


def load_sprites(sprite_name, quantity):
    """
    > Carrega uma quantidade de sprites (de nome padrão -> nome-numero.png) para dentro de uma lista
    vazia gerada.

    :param quantity: Quantidade de sprites.
    :param sprite_name: Nome do sprite até o número (ex: 'sprite-')
    :return: Lista com os sprites carregados.
    """

    if quantity > 1:
        sprites_list = list()

        for sprite_loader in range(1, quantity + 1):
            load_sprite = pygame.image.load(f'{sprite_name}{sprite_loader}.png').convert_alpha()

            sprites_list.append(load_sprite)

        return sprites_list

    else:
        sprite = pygame.image.load(f'{sprite_name}.png').convert_alpha()

        return sprite


def set_in_screen(obj, screen_d, is_foe=False, background_x=0, background_size=(0, 0)):
    """
    > Posiciona um objeto dentro da tela, a partir de sua hitbox e da largura da tela.

    :param obj: O objeto (que contenha um rect + uma hitbox) a ser posicionado.
    :param screen_d: O tamanho da tela.
    :return: Nada.
    """

    if is_foe:
        screen_right = background_x + background_size[0]
    else:
        screen_right = screen_d[0]
    screen_left = background_x

    if obj.real_rect[0] >= screen_right - obj.char_box[2]:
        obj.rect[0] = screen_right - obj.char_box[0] - obj.char_box[2]
        if is_foe:
            return 'right'

    if obj.real_rect[0] <= screen_left:
        obj.rect[0] = screen_left - obj.char_box[0]
        if is_foe:
            return 'left'


def activate_collision(player, foe, speed):

    li = [player, foe]

    for char in enumerate(li):

        half_body = li[char[0] - 1].real_rect[0] + li[char[0] - 1].char_box[2] / 2

        if li[char[0]].is_moving and not li[char[0]].is_moving_backwards:

            if li[char[0]].current_looking_right:
                if li[char[0]].real_rect[0] >= half_body - li[char[0]].char_box[2]:
                    if not li[char[0] - 1].is_crouching and not li[char[0] - 1].is_looking_up:
                        li[char[0] - 1].rect[0] += speed
                        li[char[0] - 1].is_moving = True
                        li[char[0] - 1].is_moving_backwards = True
                        li[char[0] - 1].being_pushed = True
                    else:
                        li[char[0]].dont_move = True

            else:
                if li[char[0]].real_rect[0] <= half_body:
                    if not li[char[0] - 1].is_crouching and not li[char[0] - 1].is_looking_up:
                        li[char[0] - 1].rect[0] -= speed
                        li[char[0] - 1].is_moving = True
                        li[char[0] - 1].is_moving_backwards = True
                        li[char[0] - 1].being_pushed = True
                    else:
                        li[char[0]].dont_move = True
        else:
            li[char[0] - 1].being_pushed = False


def animate_char(obj, animation_list, break_last=False, reverse=False):
    """
    > Anima um objeto de classe Character, com base em uma lista de sprites.

    :param obj: O objeto (de classe Character) a ser animado.
    :param animation_list: A lista contendo os sprites.
    :param break_last: True se a animação deve paralisar no último sprite.
    :param reverse: True se os sprites devem rodar ao contrário.
    :return: Nada.
    """

    try:
        if break_last:
            if obj.current_sprite >= len(animation_list):
                obj.current_sprite = len(animation_list) - 1

        elif reverse:
            if obj.current_sprite <= 0:
                obj.current_sprite = len(animation_list) - 1

        else:

            if obj.current_sprite >= len(animation_list):
                obj.current_sprite = 0

        obj.image = animation_list[obj.current_sprite]

        if reverse:
            obj.current_sprite -= 1
        else:
            obj.current_sprite += 1

    except IndexError:
        obj.current_sprite = 0


def load_background(screen, image, add_width=0, quantity=1):
    """
    > Carrega um background ou lista de cenas já nas dimensões ajustadas da tela.

    :param screen: A dimensão da tela.
    :param image: A imagem a ser carregada.
    :param add_width: Largura adicional para o background (para backgrounds da luta).
    :param quantity: A quantidade de frames caso queira carregar uma lista.
    :return: A imagem ou lista de imagens ajustada.
    """

    if quantity > 1:
        scenes = []

        for sprite_loader in range(1, quantity + 1):
            load_sprite = pygame.image.load(f'{image}{sprite_loader}.png').convert_alpha()
            load_sprite = pygame.transform.scale(load_sprite, (screen[0] + add_width, screen[1]))

            scenes.append(load_sprite)

        return scenes

    else:
        loaded = pygame.image.load(image)
        loaded = pygame.transform.scale(loaded, (screen[0] + add_width, screen[1]))

        return loaded
