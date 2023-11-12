import pygame
from random import randint
from pickle import dump as pickle_dump, load as pickle_load
from pyautogui import size as auto_size
from pygame.locals import *
from PP_system import tools, design, menu_t, database, fight_t, network, compression

pygame.init()
pygame.font.init()
pygame.mixer.init()


try:
    compression.extract_dir('paca-paua-compressed')
except Exception as error:
    print(error)


FULL_SCREEN = auto_size()
SCREEN_WIDTH = FULL_SCREEN[0]
SCREEN_HEIGHT = FULL_SCREEN[1]
SCREEN_DIMENSION = (SCREEN_WIDTH, SCREEN_HEIGHT)
GROUND_LIMIT = SCREEN_HEIGHT - 45
BACKGROUND = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png')

SCREEN_SCROLL_VEL = 7

CLOCK = pygame.time.Clock()
CLOCK_FPS = 33

FONTS_LIST = pygame.font.get_fonts()
NUMBERS_FONT = FONTS_LIST[FONTS_LIST.index('calisto')]
WORDS_FONT = FONTS_LIST[FONTS_LIST.index('ravie')]
CHAR_NAMES_FONT = FONTS_LIST[FONTS_LIST.index('cooperblack')]

ALL_CHAR_STS = database.get_status()
ALL_CHAR_L_MTP = database.get_multipliers(light=True)
ALL_CHAR_H_MTP = database.get_multipliers(light=False)
ALL_CHAR_U_MTP = database.get_ult_multipliers()

PLAYER_SPEED = 13
JUMP_HEIGHT = 10
DASH_SPEED = 7
DASH_RANGE = 50


screen = pygame.display.set_mode(SCREEN_DIMENSION)
pygame.display.set_caption('Paca Pauá')

game_paused = False
start_fight_system = False
fight_system_started = False
pressed_key = ''
mirrored_foe = False

current_saved_level = 1
current_save = 0

try:
    andura_mark = pickle_load(open('andura-mark.dat', 'rb'))

except FileNotFoundError:
    andura_mark = [0, '']

port = 5555
other_marks = []
mark_sent = False
receive_marks = False

client = network.Connection(port)

if not client.connected:
    client = None


pause_fight_clock = False
hide_fight_hud = False
hide_fight_clock = False
limit_fight_time = 90
rounds_quantity = 2
fight_difficult = 'normal'

fight_background_add_width = 200
fight_background_x = -fight_background_add_width / 2

fight_background_list = [tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/mata_a_background.png',
                                               add_width=fight_background_add_width),
                         tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/mata_a2_background.png',
                                               add_width=fight_background_add_width),
                         tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/cerrado_background.png',
                                               add_width=fight_background_add_width)
                         ]

fight_background_front_list = [pygame.image.load('paca-paua/sprites/backgrounds/mata_a_background_front.png'),
                               pygame.image.load('paca-paua/sprites/backgrounds/mata_a2_background_front.png'),
                               pygame.image.load('paca-paua/sprites/backgrounds/cerrado_background_front.png')]

start_this_fade = False

char_choice = ''

p_move = False
p_going_back_key = pygame.K_a
jump_command = False
p_attack_command = False
p_attack_kind = ''
p_current_char = ''
p_char_choice = ''
p_consecutive_hits = 0

f_attack_kind = ''
f_current_char = ''
f_char_choice = ''
f_consecutive_hits = 0
foe_on_limit = ''


#   standing[0] - walking[1] - jumping[2] - dashing[3] - defending[4] - dead[5] - hit[6] - crouch[7]

character_sprites = {

    'Caipora':    [tools.load_sprites('paca-paua/sprites/caipora/behaviors/idle-', 19),
                   tools.load_sprites('paca-paua/sprites/caipora/behaviors/walk-', 19),
                   tools.load_sprites('paca-paua/sprites/caipora/behaviors/jump-', 21),
                   tools.load_sprites('paca-paua/sprites/caipora/behaviors/dash-', 17),
                   tools.load_sprites('paca-paua/sprites/caipora/behaviors/defend-', 5),
                   tools.load_sprites('paca-paua/sprites/caipora/behaviors/death-', 19),
                   tools.load_sprites('paca-paua/sprites/caipora/behaviors/hit-', 13),
                   tools.load_sprites('paca-paua/sprites/caipora/behaviors/crouch-', 7)],

    'Boitata':    [tools.load_sprites('paca-paua/sprites/boitata/behaviors/idle-', 21),
                   tools.load_sprites('paca-paua/sprites/boitata/behaviors/walk-', 28),
                   tools.load_sprites('paca-paua/sprites/boitata/behaviors/jump-', 21),
                   tools.load_sprites('paca-paua/sprites/boitata/behaviors/dash-', 21),
                   tools.load_sprites('paca-paua/sprites/boitata/behaviors/defend-', 13),
                   tools.load_sprites('paca-paua/sprites/boitata/behaviors/death-', 21),
                   tools.load_sprites('paca-paua/sprites/boitata/behaviors/hit-', 11),
                   tools.load_sprites('paca-paua/sprites/boitata/behaviors/crouch-', 10)],


                    }


b_moves_sprites = {

    'Caipora':   {'Light Attacks': [tools.load_sprites('paca-paua/sprites/caipora/basic-moves/straight_strike-', 11),
                                    tools.load_sprites('paca-paua/sprites/caipora/basic-moves/rising-strike-', 13),
                                    tools.load_sprites('paca-paua/sprites/caipora/basic-moves/low-pushed-hit-', 16)],

                  'Heavy Attacks': [tools.load_sprites('paca-paua/sprites/caipora/basic-moves/quick_assault-', 15),
                                    tools.load_sprites('paca-paua/sprites/caipora/basic-moves/crescent_assault-', 15),
                                    tools.load_sprites('paca-paua/sprites/caipora/basic-moves/ground-ring-blow-', 16)]
                  },

    'Boitata':   {'Light Attacks': [tools.load_sprites('paca-paua/sprites/boitata/basic-moves/straight_strike-', 23),
                                    tools.load_sprites('paca-paua/sprites/boitata/basic-moves/rising-strike-', 21),
                                    tools.load_sprites('paca-paua/sprites/boitata/basic-moves/low-pushed-hit-', 21)],

                  'Heavy Attacks': [tools.load_sprites('paca-paua/sprites/boitata/basic-moves/quick_assault-', 21),
                                    tools.load_sprites('paca-paua/sprites/boitata/basic-moves/crescent_assault-', 21),
                                    tools.load_sprites('paca-paua/sprites/boitata/basic-moves/ground-ring-blow-', 18)]
                  }

                  }

b_moves_sounds = {'light': pygame.mixer.Sound('paca-paua/sounds/effects/Melee 1.mp3'),
                  'heavy': pygame.mixer.Sound('paca-paua/sounds/effects/Melee 2.mp3'),
                  'light_hit': pygame.mixer.Sound('paca-paua/sounds/effects/Hit 1.mp3'),
                  'heavy_hit': pygame.mixer.Sound('paca-paua/sounds/effects/Hit 2.mp3'),
                  'ultimate': pygame.mixer.Sound('paca-paua/sounds/effects/Ultimate.mp3')}


ultimates_sprites = {

    'Caipora': [tools.load_sprites('paca-paua/sprites/caipora/ultimate/FLASH ULTIMATE', 1),
                tools.load_sprites('paca-paua/sprites/caipora/ultimate/ultimate-', 8)],

    'Boitata': [tools.load_sprites('paca-paua/sprites/boitata/ultimate/FLASH ULTIMATE', 1),
                tools.load_sprites('paca-paua/sprites/boitata/ultimate/ultimate-', 57)]

                    }


class MainSystem:

    def __init__(self):

        self.playing_music = False
        self.end_server = False

        self.mode_intro = False
        self.scene_clock = 0
        self.fade_transparency = 255
        self.fade_layer = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png')
        self.fading_in = True
        self.fade_vel = 3
        self.layer_counter = 0
        self.layers_list = [tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/white square.png'),
                            tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png'),
                            tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png')]

        self.cloud_tiger_logo = pygame.image.load('paca-paua/sprites/backgrounds/logo CloudTiger.png')
        self.smaug_logo = pygame.image.load('paca-paua/sprites/backgrounds/smaug.png')
        self.fatec_logo = pygame.image.load('paca-paua/sprites/backgrounds/fatec.png')
        self.carapicuiba_logo = pygame.image.load('paca-paua/sprites/backgrounds/carapicuiba.png')

        self.mode_menu = True
        self.new_game_mode = False
        self.load_game_mode = False

        self.mode_fight = False
        self.menu_button_rect = (SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 - 75), (300, 150)
        self.menu_button = menu_t.create_button('paca-paua/sprites/menu/menu/Wooden Button.png', self.menu_button_rect)
        self.p_reset_combo = 0
        self.f_reset_combo = 0
        self.reset_combo_time = 2

        self.mode_story = False
        self.story_intro = False
        self.slide_title = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png')
        self.game_logo = pygame.image.load('paca-paua/sprites/backgrounds/Paca Paua Logo 2.png')

        self.text_object = pygame.font.SysFont(WORDS_FONT, 40)
        self.text_display = None
        self.text_display_2 = None
        self.text_counter = 0
        self.char_counter = 0
        self.text = '        '
        self.text_getter = []
        self.text_getter_2 = []
        self.reset_clock = False
        self.pause_char_add = False
        self.back_to_text = False
        self.cutscene_end = False

        self.cutscene_1_layers = {
            'Scene_1': [tools.load_background(SCREEN_DIMENSION,
                                              'paca-paua/sprites/cutscenes/cutscene1/scene_1/street.png'),
                        tools.load_background(SCREEN_DIMENSION,
                                              'paca-paua/sprites/cutscenes/cutscene1/scene_1/ambulance.png')],

            'Scene_2': [tools.load_background(SCREEN_DIMENSION,
                                              'paca-paua/sprites/cutscenes/cutscene1/scene_2/clouds.png'),
                        tools.load_background(SCREEN_DIMENSION,
                                              'paca-paua/sprites/cutscenes/cutscene1/scene_2/back_trees.png'),
                        tools.load_background(SCREEN_DIMENSION,
                                              'paca-paua/sprites/cutscenes/cutscene1/scene_2/grass.png')]
        }

        self.cutscene_1_scenes = {
            'Scene_1': tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/cutscenes/cutscene1/scene_1/caipora-',
                                             quantity=7),

            'Scene_2': tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/cutscenes/cutscene1/scene_2/caipora-',
                                             quantity=12)
        }

        self.cutscene_slide_list = []
        self.cutscene_slide = ''
        self.slide_counter = 0

        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_on_menu = False

    def update(self):
        global BACKGROUND, GROUND_LIMIT, fight_background, p_consecutive_hits, f_consecutive_hits

        if not self.playing_music:
            self.playing_music = True

            if self.mode_menu and not menu.char_selection and not menu.andura and not menu.tutorial:
                pygame.mixer.music.load('paca-paua/sounds/musics/Menu.mp3')
                pygame.mixer.music.play(loops=-1)

            elif self.mode_menu and menu.char_selection:
                pygame.mixer.music.load('paca-paua/sounds/musics/Char Selection.mp3')
                pygame.mixer.music.play(loops=-1)

            elif self.mode_menu and menu.andura:
                pygame.mixer.music.load('paca-paua/sounds/musics/Andura.mp3')
                pygame.mixer.music.play(loops=-1)

            elif self.mode_menu and menu.tutorial:
                pygame.mixer.music.load('paca-paua/sounds/musics/Cuca Theme Song.mp3')
                pygame.mixer.music.play(loops=-1)

            elif self.mode_story and not self.mode_fight:
                pygame.mixer.music.load('paca-paua/sounds/musics/Cutscene.mp3')
                pygame.mixer.music.play(loops=-1)

            elif self.mode_fight:
                if fight_background == fight_background_list[0]:
                    pygame.mixer.music.load('paca-paua/sounds/musics/Boitatá theme song.mp3')
                elif fight_background == fight_background_list[1]:
                    pygame.mixer.music.load('paca-paua/sounds/musics/Saci Theme Song.mp3')
                else:
                    pygame.mixer.music.load('paca-paua/sounds/musics/Mula Theme Song.mp3')
                pygame.mixer.music.play(loops=-1)
            else:
                pygame.mixer.music.stop()
                self.playing_music = False

        if fight_system_started and self.mode_fight:

            if fight_system.fight_clock_count == self.p_reset_combo:
                p_consecutive_hits = 0

                self.p_reset_combo = fight_system.fight_clock_count + self.reset_combo_time

            if fight_system.fight_clock_count == self.f_reset_combo:
                f_consecutive_hits = 0

                self.f_reset_combo = fight_system.fight_clock_count + self.reset_combo_time

    def get_scene_clock(self):

        self.scene_clock += 1

        if self.scene_clock >= 500:
            self.scene_clock = 500

    def intro(self, story=False):
        global BACKGROUND

        if not self.layer_counter == len(self.layers_list):
            for layer in enumerate(self.layers_list):
                if self.layer_counter == layer[0]:
                    BACKGROUND = layer[1]
        elif not BACKGROUND == self.slide_title:
            self.fade_vel = 3
            self.layer_counter = 0
        else:
            self.fade_vel = 3

        if self.layer_counter <= 0:
            screen.blit(self.smaug_logo, (SCREEN_WIDTH / 2 - 332, 80))
            screen.blit(self.fatec_logo, (SCREEN_WIDTH / 2 - 190, 451))
            screen.blit(self.carapicuiba_logo, (SCREEN_WIDTH / 2 - 290, 441))

        elif self.layer_counter == 1:
            screen.blit(self.cloud_tiger_logo, (SCREEN_WIDTH / 2 - 300, SCREEN_HEIGHT / 2 - 300))

        else:
            self.fade_vel = 9

        self.fade_layer.set_alpha(self.fade_transparency)
        screen.blit(self.fade_layer, (0, 0))

        if not self.layer_counter == len(self.layers_list):
            if self.scene_clock >= CLOCK_FPS and self.fading_in:
                self.fade_transparency -= self.fade_vel

            elif self.scene_clock >= CLOCK_FPS and not self.fading_in:
                self.fade_transparency += self.fade_vel

            if self.fade_layer.get_alpha() <= 0 and self.fading_in:
                self.scene_clock = 0
                self.fading_in = False

            elif self.fade_layer.get_alpha() >= 255 and not self.fading_in:
                self.scene_clock = 0
                self.fading_in = True
                self.layer_counter += 1

        if not story:
            if self.layer_counter == len(self.layers_list):
                self.mode_intro = False
                self.mode_menu = True
        else:
            if self.layer_counter == len(self.layers_list):
                if not BACKGROUND == self.slide_title:
                    self.scene_clock = 0
                    self.fade_transparency = 0
                BACKGROUND = self.slide_title
                screen.blit(self.game_logo, (SCREEN_WIDTH / 2 - 300, SCREEN_HEIGHT / 2 - 300))
                screen.blit(self.fade_layer, (0, 0))

                if self.scene_clock >= CLOCK_FPS * 8:
                    self.fade_transparency += self.fade_vel

                    if self.fade_layer.get_alpha() >= 255:
                        self.story_intro = False
                        self.mode_story = True
                        self.scene_clock = 0

    def pause_game(self):

        self.mouse_pos = pygame.mouse.get_pos()

        self.fade_transparency = 190
        self.fade_layer.set_alpha(self.fade_transparency)
        screen.blit(self.fade_layer, (0, 0))

        screen.blit(self.menu_button['Sprite'], self.menu_button['Rect'])

        posit = design.get_button_center(self.menu_button)
        design.display_text('MENU', WORDS_FONT, 50, 'black', posit, screen, True)

        self.mouse_on_menu = menu_t.get_mouse_collision(self, self.menu_button)

    def cutscene(self):
        global BACKGROUND, CLOCK_FPS, start_fight_system, fight_system_started, p_current_char, f_current_char,\
            fight_system_started, start_fight_system

        if current_saved_level == 1:
            CLOCK_FPS = 10

            if self.cutscene_end and self.scene_clock >= CLOCK_FPS * 4:
                CLOCK_FPS = 33
                self.mode_fight = True
                self.playing_music = False

                start_fight_system = True
                fight_system_started = False

                p_current_char = 'Caipora'
                f_current_char = 'Boitata'

            if self.text_counter >= len(self.text):
                show_cutscene = True

                if not self.back_to_text:
                    self.text_counter = -1
                    self.scene_clock = 0

                elif not self.cutscene_end:
                    self.scene_clock = 0
                    self.cutscene_end = True

            elif not self.text_counter == -1:
                show_cutscene = False
            else:
                show_cutscene = True

            if not show_cutscene:
                BACKGROUND = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png')

                if self.scene_clock >= CLOCK_FPS * 4 or self.pause_char_add:
                    if not self.back_to_text:
                        self.text = ['O Brasil enfrenta uma onda de%mortes no ano de 2020...',
                                     'Caipora, um mito encarregado de proteger%a floresta, percebe a anomalia.',
                                     'Sua empatia não permite que%ela fique parada...']
                    else:
                        self.text = ['Sendo assim, Caipora busca ajuda%em sua fonte mais próxima...',
                                     'Na Mata Atlântica, seu colega, Boitatá.%',
                                     'Conquistar essa ajuda, no entanto,%não será fácil.',
                                     'O preço dessa aliança é a%vitória em uma luta...',
                                     'Caipora aceita!%']

                    if not self.text_counter >= len(self.text) and not self.pause_char_add:
                        if self.char_counter < self.text[self.text_counter].index('%'):
                            self.text_getter.append(self.text[self.text_counter][self.char_counter])

                        elif self.text[self.text_counter][self.char_counter] != '%':
                            self.text_getter_2.append(self.text[self.text_counter][self.char_counter])
                        else:
                            self.text_getter_2.append(' ')

                    self.text_display = self.text_object.render(''.join(self.text_getter), True, design.color())
                    self.text_display_2 = self.text_object.render(''.join(self.text_getter_2), True, design.color())

                    screen.blit(self.text_display, (SCREEN_WIDTH / 2 - self.text_display.get_size()[0] / 2,
                                                    SCREEN_HEIGHT / 2 - self.text_display.get_size()[1] / 2))
                    screen.blit(self.text_display_2, (SCREEN_WIDTH / 2 - self.text_display.get_size()[0] / 2,
                                                      SCREEN_HEIGHT / 2 - self.text_display.get_size()[1] / 2 + 40))

                    if not self.pause_char_add:
                        self.char_counter += 1

                    if self.text_counter < len(self.text):
                        if self.char_counter >= len(self.text[self.text_counter]):

                            if not self.reset_clock:
                                self.scene_clock = 0
                                self.pause_char_add = True
                                self.reset_clock = True

                            if self.scene_clock >= CLOCK_FPS * 4:

                                self.text_getter.clear()
                                self.text_getter_2.clear()
                                self.text_counter += 1
                                self.char_counter = 0
                                self.reset_clock = False
                                self.pause_char_add = False

            elif not self.cutscene_end:

                if self.slide_counter >= len(self.cutscene_slide_list):
                    self.slide_counter = 0

                if self.scene_clock <= CLOCK_FPS * 7:
                    self.cutscene_slide_list = self.cutscene_1_scenes['Scene_1']
                    self.cutscene_slide = self.cutscene_slide_list[self.slide_counter]

                    screen.blit(self.cutscene_1_layers['Scene_1'][0], (0, 0))
                    screen.blit(self.cutscene_1_layers['Scene_1'][1], (0, 0))
                    screen.blit(self.cutscene_slide, (0, 0))

                elif self.scene_clock <= CLOCK_FPS * 14:
                    self.cutscene_slide_list = self.cutscene_1_scenes['Scene_2']
                    self.cutscene_slide = self.cutscene_slide_list[self.slide_counter]

                    screen.blit(self.cutscene_1_layers['Scene_2'][0], (0, 0))
                    screen.blit(self.cutscene_1_layers['Scene_2'][1], (0, 0))
                    screen.blit(self.cutscene_1_layers['Scene_2'][2], (0, 0))
                    screen.blit(self.cutscene_slide, (0, 0))

                else:
                    self.back_to_text = True
                    self.text_counter = 0

                self.slide_counter += 1

        elif current_saved_level == 2:
            self.fade_layer.set_alpha(self.fade_transparency)

            if not CLOCK_FPS == 10:
                self.scene_clock = 0
                self.text_counter = 0
                self.char_counter = 0
                self.pause_char_add = False
                self.reset_clock = False
                self.playing_music = False
                CLOCK_FPS = 10

            if self.scene_clock >= CLOCK_FPS * 3:
                fight_system_started = False
                start_fight_system = False
                BACKGROUND = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png')

            if self.scene_clock >= CLOCK_FPS * 5 or self.pause_char_add:
                self.text = ['Dessa forma, Boitatá se une%à nobre causa de Caipora.',
                             'Aqui e agora, uma longa%jornada se inicia...', 'CONTINUA!',
                             '[SALVANDO O PROGRESSO...]', '[JOGO SALVO!]']

                if not self.text_counter >= len(self.text) and not self.pause_char_add:
                    self.text_getter.append(self.text[self.text_counter][self.char_counter])

                self.text_display = self.text_object.render(''.join(self.text_getter), True, design.color())

                screen.blit(self.text_display, (SCREEN_WIDTH / 2 - self.text_display.get_size()[0] / 2,
                                                SCREEN_HEIGHT / 2 - self.text_display.get_size()[1] / 2))

                if not self.pause_char_add:
                    self.char_counter += 1

                if self.text_counter < len(self.text):
                    if self.char_counter >= len(self.text[self.text_counter]):

                        if not self.reset_clock:
                            self.scene_clock = 0
                            self.pause_char_add = True
                            self.reset_clock = True

                        if self.scene_clock >= CLOCK_FPS * 4:
                            self.text_getter.clear()
                            self.text_counter += 1
                            self.char_counter = 0
                            self.reset_clock = False
                            self.pause_char_add = False

                elif self.scene_clock >= CLOCK_FPS * 8:
                    CLOCK_FPS = 33

                    if current_save == 1:
                        pickle_dump(current_saved_level, open('save_1.dat', 'wb'))

                    elif current_save == 2:
                        pickle_dump(current_saved_level, open('save_2.dat', 'wb'))

                    self.mode_story = False
                    self.mode_menu = True
                    self.playing_music = False
                    menu.menu = True


class MenuSystem:

    def __init__(self):

        self.sounds = {'click': 'paca-paua/sounds/effects/Selection Menu Effect.mp3',
                       'confirm_fight': 'paca-paua/sounds/effects/Selection Menu Effect 2.mp3'}
        self.play_sound = pygame.mixer.Sound(self.sounds['click'])

        self.large_button_size = (330, 125)
        self.small_button_size = (200, 80)

        # _____________________________________________________________________________________________________________
        self.menu = True

        self.game_logo_rect = (SCREEN_WIDTH - 550, -70), (500, 500)
        self.game_logo = menu_t.create_button('Paca Paua Logo.png', self.game_logo_rect, path='menu')

        self.back_button_rect = (SCREEN_WIDTH - 260, SCREEN_HEIGHT - 150), self.small_button_size
        self.back_button = menu_t.create_button('Wooden Button.png', self.back_button_rect, path='menu')

        self.exit_button_rect = (SCREEN_WIDTH - 260, SCREEN_HEIGHT - 150), self.small_button_size
        self.exit_button = menu_t.create_button('Wooden Button.png', self.exit_button_rect, 'menu')

        self.new_game_button_rect = (SCREEN_WIDTH / 2 - 345, 70), self.large_button_size
        self.new_game_button = menu_t.create_button('Wooden Button.png', self.new_game_button_rect, 'menu')

        self.load_game_button_rect = (SCREEN_WIDTH / 2 - 250, 215), self.large_button_size
        self.load_game_button = menu_t.create_button('Wooden Button.png', self.load_game_button_rect, 'menu')

        self.f_fight_button_rect = (SCREEN_WIDTH / 2 - 155, 360), self.large_button_size
        self.f_fight_button = menu_t.create_button('Wooden Button.png', self.f_fight_button_rect, 'menu')

        self.tutorial_button_rect = (SCREEN_WIDTH / 2 - 60, 505), self.large_button_size
        self.tutorial_button = menu_t.create_button('Wooden Button.png', self.tutorial_button_rect, 'menu')

        self.andura_button_rect = (SCREEN_WIDTH - 223, SCREEN_HEIGHT - 250), (150, 80)
        self.andura_button = menu_t.create_button('Andura Button.png', self.andura_button_rect, 'menu')

        # _____________________________________________________________________________________________________________
        self.saves = False

        self.save_square_1_rect = (100, 50), (450, 612)
        self.save_square_1 = menu_t.create_button('Save Square.png', self.save_square_1_rect, 'saves')

        self.save_square_2_rect = (590, 50), (450, 612)
        self.save_square_2 = menu_t.create_button('Save Square.png', self.save_square_2_rect, 'saves')

        self.accept_button_rect = (SCREEN_WIDTH - 260, SCREEN_HEIGHT - 250), self.small_button_size
        self.accept_button = menu_t.create_button('Wooden Button.png', self.accept_button_rect, 'menu')

        # _____________________________________________________________________________________________________________
        self.char_selection = False

        self.player_selection = False
        self.foe_selection = False
        self.player_selected = False
        self.foe_selected = False

        self.chars_selected = 0

        self.pause_clock_button_rect = (SCREEN_WIDTH - 430, 190), (300, 80)
        self.pause_clock_button = menu_t.create_button('Wooden Button.png', self.pause_clock_button_rect, 'menu')

        self.difficult_button_rect = (SCREEN_WIDTH - 430, 290), (300, 80)
        self.difficult_button = menu_t.create_button('Wooden Button.png', self.difficult_button_rect, 'menu')

        self.confirm_button_rect = (SCREEN_WIDTH - 430, 90), (300, 80)
        self.confirm_button = menu_t.create_button('Wooden Button.png', self.confirm_button_rect, 'menu')

        self.caipora_button_rect = (130, 100), (200, 200)
        self.caipora_button = menu_t.create_button('Caipora Button.png', self.caipora_button_rect, 'char-selection')

        self.boitata_button_rect = (360, 100), (200, 200)
        self.boitata_button = menu_t.create_button('Boitata Button.png', self.boitata_button_rect, 'char-selection')

        # _____________________________________________________________________________________________________________
        self.andura = False

        self.andura_tree_rect = (SCREEN_WIDTH / 2 - 500, 0), (1000, SCREEN_HEIGHT)
        self.andura_tree = menu_t.create_button('paca-paua/sprites/menu/andura/Andurá.png', self.andura_tree_rect)

        self.black_rect_rect = (0, SCREEN_HEIGHT - 130), (SCREEN_WIDTH, 130)
        self.black_rect = menu_t.create_button('paca-paua/sprites/backgrounds/black square.png', self.black_rect_rect)

        self.yes_button_rect = (SCREEN_WIDTH - 560, SCREEN_HEIGHT - 110), (80, 35)
        self.yes_button = menu_t.create_button('Wooden Square Button.png', self.yes_button_rect, 'menu')

        self.no_button_rect = (SCREEN_WIDTH - 560, SCREEN_HEIGHT - 65), (80, 35)
        self.no_button = menu_t.create_button('Wooden Square Button.png', self.no_button_rect, 'menu')

        self.writing_rect_rect = (SCREEN_WIDTH / 2 - 125, SCREEN_HEIGHT / 2 - 30), (250, 60)
        self.writing_rect = menu_t.create_button('paca-paua/sprites/menu/andura/Andura write chart.png',
                                                 self.writing_rect_rect)

        self.andura_write_mode = False
        self.andura_user_writing = False
        self.andura_mark_txt = []

        self.letters = {pygame.K_q: 'Q', pygame.K_w: 'W', pygame.K_e: 'E', pygame.K_r: 'R', pygame.K_t: 'T',
                        pygame.K_y: 'Y', pygame.K_u: 'U', pygame.K_i: 'I', pygame.K_o: 'O', pygame.K_p: 'P',
                        pygame.K_a: 'A', pygame.K_s: 'S', pygame.K_d: 'D', pygame.K_f: 'F', pygame.K_g: 'G',
                        pygame.K_h: 'H', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L', pygame.K_z: 'Z',
                        pygame.K_x: 'X', pygame.K_c: 'C', pygame.K_v: 'V', pygame.K_b: 'B', pygame.K_n: 'N',
                        pygame.K_m: 'M'}

        # _____________________________________________________________________________________________________________
        self.tutorial = False

        self.next_button_rect = (SCREEN_WIDTH - 260, SCREEN_HEIGHT - 250), self.small_button_size
        self.next_button = menu_t.create_button('Wooden Button.png', self.next_button_rect, 'menu')

        self.tutorial_slide = 1

        self.tutorial_slide_1 = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/menu/tutorial/Slide 1.png')
        self.tutorial_slide_2 = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/menu/tutorial/Slide 2.png')
        self.tutorial_slide_3 = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/menu/tutorial/Slide 3.png')
        self.tutorial_slide_4 = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/menu/tutorial/Slide 4.png')

        # _____________________________________________________________________________________________________________
        self.current_background = tools.load_background(SCREEN_DIMENSION,
                                                        'paca-paua/sprites/backgrounds/black square.png')

        self.mouse_pos = pygame.mouse.get_pos()

        self.mouse_on = {'exit': False, 'new_game': False, 'load_game': False, 'f_fight': False,
                         'tutorial': False, 'andura': False,

                         'save_1': False, 'save_2': False, 'accept': False,

                         'back': False, 'pause_clock': False, 'confirm': False, 'difficult': False,
                         'caipora': False, 'boitata': False,

                         'yes_andura': False, 'no_andura': False, 'writing': False,

                         'next': False}

        self.buttons = {'exit': self.exit_button, 'new_game': self.new_game_button,
                        'load_game': self.load_game_button, 'f_fight': self.f_fight_button,
                        'tutorial': self.tutorial_button, 'andura': self.andura_button,

                        'save_1': self.save_square_1, 'save_2': self.save_square_2,
                        'accept': self.accept_button,

                        'back': self.back_button, 'pause_clock': self.pause_clock_button,
                        'confirm': self.confirm_button, 'difficult': self.difficult_button,
                        'caipora': self.caipora_button, 'boitata': self.boitata_button,

                        'yes_andura': self.yes_button, 'no_andura': self.no_button,
                        'writing': self.writing_rect,

                        'next': self.next_button}
        # _____________________________________________________________________________________________________________

    def update(self):
        global BACKGROUND

        BACKGROUND = self.current_background

        if not self.andura and not self.tutorial:
            self.current_background = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/Menu.png')
        elif self.andura:
            self.current_background = tools.load_background(SCREEN_DIMENSION,
                                                            'paca-paua/sprites/backgrounds/andura background.png')
        else:
            self.current_background = tools.load_background(SCREEN_DIMENSION,
                                                            'paca-paua/sprites/backgrounds/black square.png')

        self.mouse_pos = pygame.mouse.get_pos()

        menu_t.get_all_mouse_collision(self, self.buttons, self.mouse_on)

    def display_menu(self):

        if self.menu:
            menu_t.blit_buttons(screen, self.f_fight_button, self.exit_button, self.new_game_button,
                                self.load_game_button, self.tutorial_button, self.andura_button)

            screen.blit(self.game_logo['Sprite'], self.game_logo['Pos'])

        # _____________________________________________________________________________________________________________
            posit = design.get_button_center(self.new_game_button)[0], \
                design.get_button_center(self.new_game_button)[1] - 20

            design.display_text('Novo', WORDS_FONT, 45, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.new_game_button)[0], \
                design.get_button_center(self.new_game_button)[1] + 20

            design.display_text('Jogo', WORDS_FONT, 45, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________
            posit = design.get_button_center(self.load_game_button)[0], \
                design.get_button_center(self.load_game_button)[1] - 20

            design.display_text('Retomar', WORDS_FONT, 45, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.load_game_button)[0], \
                design.get_button_center(self.load_game_button)[1] + 20

            design.display_text('Jogo', WORDS_FONT, 45, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________
            posit = design.get_button_center(self.f_fight_button)[0], \
                design.get_button_center(self.f_fight_button)[1] - 20

            design.display_text('Luta', WORDS_FONT, 45, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.f_fight_button)[0], \
                design.get_button_center(self.f_fight_button)[1] + 20

            design.display_text('Livre', WORDS_FONT, 45, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________

            posit = design.get_button_center(self.tutorial_button)

            design.display_text('Tutorial', WORDS_FONT, 45, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________
            posit = design.get_button_center(self.exit_button)

            design.display_text('Sair', WORDS_FONT, 30, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________

        elif self.saves:
            menu_t.blit_buttons(screen, self.save_square_1, self.save_square_2, self.back_button,
                                self.accept_button)

            posit = design.get_button_center(self.back_button)
            design.display_text('Voltar', WORDS_FONT, 30, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.accept_button)
            design.display_text('Aceitar', WORDS_FONT, 30, 'black', posit, screen, centralize=True)

            posit = (design.get_button_center(self.save_square_1)[0],
                     design.get_button_center(self.save_square_1)[1] - 150)
            design.display_text('Save 1', WORDS_FONT, 80, 'black', posit, screen, centralize=True)

            posit = (design.get_button_center(self.save_square_2)[0],
                     design.get_button_center(self.save_square_2)[1] - 150)
            design.display_text('Save 2', WORDS_FONT, 80, 'black', posit, screen, centralize=True)

            try:
                level_txt_1 = ('Fase:', str(pickle_load(open('save_1.dat', 'rb'))))
            except FileNotFoundError:
                level_txt_1 = ('', '')

            try:
                level_txt_2 = ('Fase:', str(pickle_load(open('save_2.dat', 'rb'))))
            except FileNotFoundError:
                level_txt_2 = ('', '')

            posit = (design.get_button_center(self.save_square_1)[0],
                     design.get_button_center(self.save_square_1)[1] + 65)
            design.display_text(level_txt_1[0], WORDS_FONT, 80, 'black', posit, screen, centralize=True)

            posit = (design.get_button_center(self.save_square_1)[0],
                     design.get_button_center(self.save_square_1)[1] + 165)
            design.display_text(level_txt_1[1], WORDS_FONT, 80, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________
            posit = (design.get_button_center(self.save_square_2)[0],
                     design.get_button_center(self.save_square_2)[1] + 65)
            design.display_text(level_txt_2[0], WORDS_FONT, 80, 'black', posit, screen, centralize=True)

            posit = (design.get_button_center(self.save_square_2)[0],
                     design.get_button_center(self.save_square_2)[1] + 165)
            design.display_text(level_txt_2[1], WORDS_FONT, 80, 'black', posit, screen, centralize=True)

        elif self.char_selection:
            self.current_background = tools.load_background(SCREEN_DIMENSION,
                                                            'paca-paua/sprites/backgrounds/Character-Selection.png')

            if pause_fight_clock:
                clock_txt = '---'
            else:
                clock_txt = '60'

            if self.chars_selected == 2:
                confirm_txt = 'Começar!'
            else:
                confirm_txt = 'Confirmar'

            if fight_difficult == 'normal':
                difficult_txt = 'Normal'
            else:
                difficult_txt = 'Difícil'

            menu_t.blit_buttons(screen, self.caipora_button, self.boitata_button, self.confirm_button,
                                self.back_button, self.pause_clock_button, self.difficult_button)

            posit = design.get_button_center(self.back_button)
            design.display_text('Voltar', WORDS_FONT, 30, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.confirm_button)
            design.display_text(confirm_txt, WORDS_FONT, 30, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________
            posit = (design.get_button_center(self.pause_clock_button)[0] + 80,
                     design.get_button_center(self.pause_clock_button)[1] + 5)

            design.display_text(clock_txt, WORDS_FONT, 30, 'black', posit, screen, centralize=True)

            posit = (design.get_button_center(self.pause_clock_button)[0] - 45,
                     design.get_button_center(self.pause_clock_button)[1] + 5)

            design.display_text('Tempo:', WORDS_FONT, 30, 'black', posit, screen, centralize=True)

        # _____________________________________________________________________________________________________________
            posit = design.get_button_center(self.difficult_button)
            design.display_text(difficult_txt, WORDS_FONT, 30, 'black', posit, screen, centralize=True)

        elif self.andura:

            menu_t.blit_buttons(screen, self.andura_tree, self.black_rect, self.yes_button,
                                self.no_button, self.back_button)

            if andura_mark[0] == 1:
                posit = (SCREEN_WIDTH / 2 + 10, SCREEN_HEIGHT / 2 - 300)
                design.display_text(andura_mark[1], WORDS_FONT, 25, 'black', posit, screen, centralize=True)

            if len(other_marks) > 0:
                increasing = 250

                for mark in other_marks:

                    posit = (SCREEN_WIDTH / 2 + 10, SCREEN_HEIGHT / 2 - increasing)
                    design.display_text(mark, WORDS_FONT, 25, 'black', posit, screen, centralize=True)
                    increasing -= 50

            posit = design.get_button_center(self.back_button)
            design.display_text('Voltar', WORDS_FONT, 30, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.yes_button)
            design.display_text('SIM', WORDS_FONT, 15, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.no_button)
            design.display_text('NÃO', WORDS_FONT, 15, 'black', posit, screen, centralize=True)

            posit = (60, self.black_rect['Pos'][1] + 20)
            andura_txt = 'As chamas de Andurá o evocam...'
            design.display_text(andura_txt, WORDS_FONT, 30, 'white', posit, screen, centralize=False)

            posit = (60, self.black_rect['Pos'][1] + 60)
            andura_txt = 'Deseja deixar a sua marca?'
            design.display_text(andura_txt, WORDS_FONT, 30, 'white', posit, screen, centralize=False)

            if self.andura_write_mode:
                black_layer = tools.load_background(SCREEN_DIMENSION, 'paca-paua/sprites/backgrounds/black square.png')
                black_layer.set_alpha(200)

                screen.blit(black_layer, (0, 0))
                screen.blit(self.writing_rect['Sprite'], self.writing_rect['Pos'])

                design.display_text('Deixe sua marca!', WORDS_FONT, 30, 'white',
                                    (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60), screen, True)

                design.display_text('Pressione o ESPAÇO para confirmar.', WORDS_FONT, 30, 'white',
                                    (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60), screen, True)

                posit = design.get_button_center(self.writing_rect)
                design.display_text(''.join(self.andura_mark_txt), WORDS_FONT, 25, 'black', posit, screen,
                                    centralize=True)

        elif self.tutorial:

            if self.tutorial_slide <= 1:
                screen.blit(self.tutorial_slide_1, (0, 0))
            elif self.tutorial_slide == 2:
                screen.blit(self.tutorial_slide_2, (0, 0))
            elif self.tutorial_slide == 3:
                screen.blit(self.tutorial_slide_3, (0, 0))
            else:
                screen.blit(self.tutorial_slide_4, (0, 0))

            menu_t.blit_buttons(screen, self.back_button, self.next_button)

            posit = design.get_button_center(self.back_button)
            design.display_text('Voltar', WORDS_FONT, 30, 'black', posit, screen, centralize=True)

            posit = design.get_button_center(self.next_button)
            design.display_text('Próximo', WORDS_FONT, 30, 'black', posit, screen, centralize=True)


class FightSystem:

    def __init__(self, f_player, foe):

        self.player = f_player
        self.foe = foe

        self.player_hp = ALL_CHAR_STS[player.character]['HP']
        self.player_atk = ALL_CHAR_STS[player.character]['ATK']

        self.player_energy = 0

        self.foe_hp = ALL_CHAR_STS[enemy.character]['HP']
        self.foe_atk = ALL_CHAR_STS[enemy.character]['ATK']

        self.p_hp_register = self.player_hp
        self.f_hp_register = self.foe_hp

        self.hard_mode_multiplier = 1.6

        if fight_difficult == 'hard':
            self.foe_atk *= self.hard_mode_multiplier

        self.foe_energy = 0

        self.player_being_hit = False
        self.foe_being_hit = False
        self.player_is_dead = False
        self.foe_is_dead = False

        self.l_attack_types = ['Straight Strike', 'Rising Strike', 'Low Pushed Hit']
        self.h_attack_types = ['Quick Assault', 'Crescent Assault', 'Ground Ring Blow']

        self.p_hit_validate = False
        self.f_hit_validate = False

        self.fight_clock = 0
        self.fight_clock_count = 0
        self.fight_anim_clock = 0
        self.fight_anim_clock_count = 0

        self.player_name_object = pygame.font.SysFont(CHAR_NAMES_FONT, 35)
        self.player_name_display = None
        self.foe_name_object = pygame.font.SysFont(CHAR_NAMES_FONT, 35)
        self.foe_name_display = None

        self.winner_name_object = pygame.font.SysFont(WORDS_FONT, 90)
        self.winner_name_display = None

        self.current_round_object = pygame.font.SysFont(WORDS_FONT, 80)
        self.current_round_display = None

        self.player_wins_object = pygame.font.SysFont(CHAR_NAMES_FONT, 40)
        self.player_wins_display = None
        self.foe_wins_object = pygame.font.SysFont(CHAR_NAMES_FONT, 40)
        self.foe_wins_display = None

        self.current_round_back = pygame.image.load('paca-paua/sprites/fight-hud/Fight Back Slider.png')
        self.current_round_back_size = (570, 160)
        self.current_round_back = pygame.transform.scale(self.current_round_back, self.current_round_back_size)
        self.current_round_back_x = -self.current_round_back_size[0]
        self.current_round_back_vel = 18
        self.current_round_back_y = SCREEN_HEIGHT / 2 - self.current_round_back_size[1] - 20
        self.current_round_transparency = 255

        self.fight_time_display_object = pygame.font.SysFont(NUMBERS_FONT, 50)
        self.fight_time_display = None
        self.fight_time_pos = (SCREEN_WIDTH / 2 - 25, 25)

        self.fight_round = 0
        self.fight_round_over = False
        self.reset_round = False
        self.update_round_info = False
        self.fight_round_fade = tools.load_background(SCREEN_DIMENSION,
                                                      'paca-paua/sprites/backgrounds/black square.png')
        self.fight_round_fade_vel = 10
        self.fight_round_fade_x = -SCREEN_WIDTH

        self.story_mode = False
        self.fight_start = False
        self.fight_pause = False
        self.fight_happening = False
        self.fight_over = False

        self.winner = ''
        self.player_wins = 0
        self.foe_wins = 0

        self.life_bar_outline_size = (int(SCREEN_WIDTH / 2 - 100), 80)
        self.ult_bar_outline_size = (int(self.life_bar_outline_size[0] - self.life_bar_outline_size[0] / 2), 50)

        self.p_life_bar_outline = pygame.image.load('paca-paua/sprites/fight-hud/life-bar.png').convert_alpha()
        self.p_life_bar_outline = pygame.transform.scale(self.p_life_bar_outline, self.life_bar_outline_size)

        self.p_ult_bar_outline = pygame.image.load('paca-paua/sprites/fight-hud/special-bar.png').convert_alpha()
        self.p_ult_bar_outline = pygame.transform.scale(self.p_ult_bar_outline, self.ult_bar_outline_size)

        self.f_life_bar_outline = self.p_life_bar_outline
        self.f_life_bar_outline = pygame.transform.flip(self.f_life_bar_outline, True, False)

        self.f_ult_bar_outline = self.p_ult_bar_outline
        self.f_ult_bar_outline = pygame.transform.flip(self.f_ult_bar_outline, True, False)

        self.p_life_bar_outline_rect = self.p_life_bar_outline.get_bounding_rect()
        self.f_life_bar_outline_rect = self.f_life_bar_outline.get_bounding_rect()

        self.p_ult_bar_outline_rect = self.p_ult_bar_outline.get_bounding_rect()
        self.f_ult_bar_outline_rect = self.f_ult_bar_outline.get_bounding_rect()

        self.p_life_bar_outline_pos = (50, 15)
        self.f_life_bar_outline_pos = (SCREEN_WIDTH - self.life_bar_outline_size[0] - 50, 15)

        self.p_ult_bar_outline_pos = (self.p_life_bar_outline_pos[0] + self.p_life_bar_outline_rect[2] / 2,
                                      self.p_life_bar_outline_pos[1] + self.p_life_bar_outline_rect[3])

        self.f_ult_bar_outline_pos = (self.f_life_bar_outline_pos[0],
                                      self.f_life_bar_outline_pos[1] + self.f_life_bar_outline_rect[3])

        self.energy_max = 20
        self.energy_proportion = self.ult_bar_outline_size[0] / self.energy_max

        self.p_life_size = self.life_bar_outline_size[0]
        self.p_life_proportion = self.p_life_size / self.player_hp

        self.p_life_shadow = self.p_life_size
        self.p_life_shadow_timer = 0
        self.p_life_shadow_start = False
        self.p_life_shadow_x = self.p_life_bar_outline_rect[0]

        self.f_life_size = self.life_bar_outline_size[0]
        self.f_life_proportion = self.f_life_size / self.foe_hp

        self.f_life_shadow = self.f_life_size
        self.f_life_shadow_timer = 0
        self.f_life_shadow_start = False
        self.f_life_shadow_x = self.f_life_bar_outline_rect[0]

        self.p_life_bar_back_rect = ([self.p_life_bar_outline_rect[0] + self.p_life_bar_outline_pos[0],
                                     self.p_life_bar_outline_pos[1] + self.life_bar_outline_size[1] / 2],
                                     [self.p_life_size, self.life_bar_outline_size[1] / 2 - 3])

        self.f_life_bar_back_rect = ([self.f_life_bar_outline_rect[0] + self.f_life_bar_outline_pos[0],
                                      self.f_life_bar_outline_pos[1] + self.life_bar_outline_size[1] / 2],
                                     [self.f_life_size, self.life_bar_outline_size[1] / 2 - 3])

        self.p_ult_bar_back_rect = ([self.p_ult_bar_outline_rect[0] + self.p_ult_bar_outline_pos[0] + 2,
                                    self.p_ult_bar_outline_rect[1] + self.p_ult_bar_outline_pos[1] + 2],
                                    [self.p_ult_bar_outline_rect[2] - 2, self.p_ult_bar_outline_rect[3] - 2])

        self.f_ult_bar_back_rect = ([self.f_ult_bar_outline_rect[0] + self.f_ult_bar_outline_pos[0] + 2,
                                     self.f_ult_bar_outline_rect[1] + self.f_ult_bar_outline_pos[1] + 2],
                                    [self.f_ult_bar_outline_rect[2] - 2, self.f_ult_bar_outline_rect[3] - 2])

    def update(self):

        if self.fight_happening:

            if pygame.sprite.collide_mask(self.player, self.foe):
                if self.player.is_attacking:
                    self.foe_being_hit = True
                    self.f_life_shadow_timer = 0
                else:
                    self.foe_being_hit = False
                    self.p_hit_validate = False

                if self.foe.is_attacking:
                    self.player_being_hit = True
                    self.p_life_shadow_timer = 0
                else:
                    self.player_being_hit = False
                    self.f_hit_validate = False

            if self.player_hp <= 0:
                self.player_is_dead = True
            else:
                self.player_is_dead = False

            if self.foe_hp <= 0:
                self.foe_is_dead = True
            else:
                self.foe_is_dead = False

        self.p_life_shadow_timer += 1
        self.f_life_shadow_timer += 1

        if self.p_life_shadow_timer >= CLOCK_FPS:
            self.p_life_shadow_timer = CLOCK_FPS
        if self.f_life_shadow_timer >= CLOCK_FPS:
            self.f_life_shadow_timer = CLOCK_FPS

        if self.p_life_shadow_timer >= 10:
            self.p_life_shadow_start = True
        if self.f_life_shadow_timer >= 10:
            self.f_life_shadow_start = True

        if int(self.p_life_shadow) == int(self.p_life_size):
            self.p_life_shadow_start = False
            self.p_life_shadow = self.p_life_size
            self.p_life_shadow_x = self.p_life_bar_outline_rect[0]

        if int(self.f_life_shadow) == int(self.f_life_size):
            self.f_life_shadow_start = False
            self.f_life_shadow = self.f_life_size
            self.f_life_shadow_x = self.f_life_bar_outline_rect[0]

        if self.fight_happening:
            if not self.fight_over and self.fight_round_over:

                if player.is_dead and player.current_sprite == len(player.dead_sprites) - 1:
                    activate_this = True
                elif enemy.is_dead and enemy.current_sprite == len(enemy.dead_sprites) - 1:
                    activate_this = True
                elif self.winner == 'none':
                    activate_this = True
                else:
                    activate_this = False

                if activate_this:
                    player.is_moving = False
                    enemy.is_moving = False
                    player.being_hit = False
                    enemy.being_hit = False

                    self.fight_anim_clock = 0
                    self.fight_anim_clock_count = 0
                    self.fight_round_fade_x = -SCREEN_WIDTH

                    self.fight_round_over = False
                    self.fight_pause = True
                    self.fight_happening = False

    def update_rules(self):
        global game_paused, p_consecutive_hits, f_consecutive_hits, current_saved_level

        if self.player_being_hit and not self.f_hit_validate or self.player_being_hit and\
                not ultimate_system.f_ult_hit_validate:
            fight_t.activate_rules(self, f_attack_kind, player, player=True)

            if f_attack_kind in self.l_attack_types:
                b_moves_sounds['light_hit'].play()
            else:
                b_moves_sounds['heavy_hit'].play()

            self.f_hit_validate = True
            ultimate_system.f_ult_hit_validate = True
            f_consecutive_hits += 1
            main.f_reset_combo = fight_system.fight_clock_count + main.reset_combo_time

            if self.f_hit_validate and enemy.is_attacking and not player.is_dead and\
                    not player.is_dashing or ultimate_system.ult_collided:
                player.is_moving = False
                self.player.being_hit = True
                self.player.current_sprite = 0

        if self.p_life_shadow_start:
            self.p_life_shadow -= ((self.p_life_shadow - self.p_life_size) / 10)
            self.p_life_shadow_x += ((self.p_life_bar_outline_rect[0] - self.p_life_shadow_x) / 10)

        if self.foe_being_hit and not self.p_hit_validate or self.foe_being_hit and \
                not ultimate_system.p_ult_hit_validate:
            fight_t.activate_rules(self, p_attack_kind, enemy, player=False)

            if p_attack_kind in self.l_attack_types:
                b_moves_sounds['light_hit'].play()
            else:
                b_moves_sounds['heavy_hit'].play()

            self.p_hit_validate = True
            ultimate_system.p_ult_hit_validate = True
            p_consecutive_hits += 1
            main.p_reset_combo = fight_system.fight_clock_count + main.reset_combo_time

            if self.p_hit_validate and player.is_attacking and not enemy.is_dead and\
                    not enemy.is_dashing or ultimate_system.ult_collided:
                enemy.is_moving = False
                self.foe.being_hit = True
                if not enemy.is_jumping:
                    self.foe.current_sprite = 0

        if self.f_life_shadow_start:
            self.f_life_shadow -= ((self.f_life_shadow - self.f_life_size) / 10)

        if self.fight_happening:

            if not self.fight_over:

                if self.player_is_dead:
                    self.fight_round_over = True
                    self.winner = 'foe'

                elif self.foe_is_dead:
                    self.fight_round_over = True
                    self.winner = 'player'

                elif self.fight_clock_count >= limit_fight_time:
                    self.fight_round_over = True

                    if self.player_hp > self.foe_hp:
                        self.winner = 'player'
                        self.foe_hp = 0
                        self.f_life_size = 3
                        self.f_life_shadow_timer = 0
                        self.foe_is_dead = True

                    elif self.foe_hp > self.player_hp:
                        self.winner = 'foe'
                        self.player_hp = 0
                        self.p_life_size = 0
                        self.p_life_bar_outline_rect[0] = self.life_bar_outline_size[0] - 3
                        self.p_life_shadow_timer = 0
                        self.player_is_dead = True

                    else:
                        self.winner = 'none'

            else:
                if self.winner == 'foe' or self.winner == 'player':
                    if not (main.mode_story and self.winner == 'player'):
                        game_paused = True
                    else:
                        main.mode_fight = False
                        current_saved_level += 1

    def get_fight_clock(self):

        if self.fight_happening:

            self.fight_clock += 1

            if self.fight_clock >= CLOCK_FPS:
                self.fight_clock = 0
                self.fight_clock_count += 1

            if pause_fight_clock:
                if self.fight_clock_count >= limit_fight_time - 3:
                    self.fight_clock_count = 0

            if self.fight_clock_count >= limit_fight_time:
                self.fight_clock_count = limit_fight_time

        self.fight_anim_clock += 1
        if self.fight_anim_clock >= CLOCK_FPS:
            self.fight_anim_clock = 0
            self.fight_anim_clock_count += 1

        if self.fight_anim_clock_count >= 60:
            self.fight_anim_clock_count = 60

    def bugs_fix(self, f_player, foe):

        if self.fight_happening:
            if not foe.is_attacking:
                self.player_being_hit = False
            if not f_player.is_attacking:
                self.foe_being_hit = False

        elif not self.fight_over:
            if not self.fight_start or not self.fight_pause:
                if player.rect[1] != player_saved_position[1]:
                    player.rect[1] = player_saved_position[1]
                if enemy.rect[1] != foe_saved_position[1]:
                    enemy.rect[1] = foe_saved_position[1]
            if not self.fight_pause and not ultimate_system.init and not ultimate_system.activated:
                if player.rect[0] != player_saved_position[0]:
                    player.rect[0] = player_saved_position[0]
                if enemy.rect[0] != foe_saved_position[0]:
                    enemy.rect[0] = foe_saved_position[0]

        if self.f_life_size < 3:
            self.f_life_size = 3

    def change_rounds(self):

        if self.fight_anim_clock_count >= 11 and self.fight_pause:
            self.fight_pause = False
            self.fight_start = True

        if self.fight_start:
            if self.winner == '':
                self.fight_happening = True
                self.update_round_info = True
                self.reset_round = True

                self.fight_start = False
            else:
                if self.fight_clock > 0:
                    self.update_round_info = True
                    self.reset_round = True
                    self.fight_anim_clock = 0
                    self.fight_anim_clock_count = 0

                if self.fight_anim_clock_count >= 11:
                    self.fight_happening = True
                    self.fight_start = False

        if self.update_round_info:
            self.fight_clock = 0
            self.fight_clock_count = 0
            if self.winner != '':
                self.fight_round += 1

            if self.winner == 'player':
                self.player_wins += 1
            elif self.winner == 'foe':
                self.foe_wins += 1

            self.update_round_info = False

        if not self.fight_round >= rounds_quantity or not self.player_wins != self.foe_wins:
            if self.reset_round:

                self.player_hp = ALL_CHAR_STS[player.character]['HP']
                self.player_atk = ALL_CHAR_STS[player.character]['ATK']

                self.foe_hp = ALL_CHAR_STS[enemy.character]['HP']
                self.foe_atk = ALL_CHAR_STS[enemy.character]['ATK']

                self.f_life_size = self.life_bar_outline_size[0]
                self.p_life_size = self.life_bar_outline_size[0]
                self.f_life_shadow = self.f_life_size
                self.p_life_shadow = self.p_life_size
                self.f_life_shadow_x = self.f_life_bar_outline_rect[0]
                self.p_life_shadow_x = self.p_life_bar_outline_rect[0]
                self.p_life_bar_outline_rect = self.p_life_bar_outline.get_bounding_rect()
                self.f_life_bar_outline_rect = self.f_life_bar_outline.get_bounding_rect()

                self.p_ult_bar_outline_rect = self.p_ult_bar_outline.get_bounding_rect()
                self.f_ult_bar_outline_rect = self.f_ult_bar_outline.get_bounding_rect()

                player.is_dead = False
                self.player_is_dead = False
                player.break_commands = False

                enemy.is_dead = False
                self.foe_is_dead = False
                enemy.break_commands = False

                player.rect[0] = player_saved_position[0]
                enemy.rect[0] = foe_saved_position[0]
                player.rect[1] = player_saved_position[1]
                enemy.rect[1] = foe_saved_position[1]

                self.current_round_back_x = -self.current_round_back_size[0]
                self.current_round_transparency = 255
                global start_this_fade, fight_background_x
                start_this_fade = False
                fight_background_x = -fight_background_add_width / 2

                self.reset_round = False
        else:
            self.fight_over = True

            if self.player_wins > self.foe_wins:
                self.winner = 'player'
            else:
                self.winner = 'foe'

    def starting_round_animation(self):
        global start_this_fade

        condition_1 = self.fight_anim_clock_count == 3 and self.fight_anim_clock >= CLOCK_FPS / 2 - 15\
            or self.fight_anim_clock_count == 4 and self.fight_anim_clock <= CLOCK_FPS / 2
        condition_2 = self.fight_anim_clock_count == 8 and self.fight_anim_clock >= CLOCK_FPS / 2 - 15\
            or self.fight_anim_clock_count == 9 and self.fight_anim_clock <= CLOCK_FPS / 2

        if condition_1 or condition_2:
            self.current_round_back_vel = 2
            start_this_fade = True
        else:
            self.current_round_back_vel = 26

        start_this_again = False
        round_number_color = design.color('black')

        if self.fight_anim_clock_count < 6:
            round_init_message = f'ROUND {self.fight_round + 1}!'
        else:
            if self.fight_anim_clock_count == 6:
                start_this_again = True
            round_init_message = 'LUTEM!'

        if start_this_again:
            self.current_round_back_x = -self.current_round_back_size[0]
            self.current_round_transparency = 255
            start_this_fade = False

        screen.blit(self.current_round_back, (self.current_round_back_x, self.current_round_back_y))

        if self.fight_anim_clock_count >= 2:
            self.current_round_back_x += self.current_round_back_vel

        if self.current_round_back_x >= SCREEN_WIDTH + 40:
            self.current_round_back_x = SCREEN_WIDTH + 40

        self.current_round_display = self.current_round_object.render(round_init_message, True, round_number_color)
        round_msg_pos = (self.current_round_back_x + self.current_round_back_size[0] / 2
                         - self.current_round_display.get_size()[0] / 2, self.current_round_back_y
                         + self.current_round_back_size[1] / 2
                         - self.current_round_display.get_size()[1] / 2)

        screen.blit(self.current_round_display, round_msg_pos)

        self.current_round_display.set_alpha(self.current_round_transparency)
        self.current_round_back.set_alpha(self.current_round_transparency)

        if start_this_fade and not condition_1 and not condition_2:
            self.current_round_transparency -= 5

    def ending_round_animation(self, end=False):
        from random import choice
        global p_attack_command, f_attack_kind, p_attack_kind

        winner_name_color = design.color('dark red')
        fight_over_color = design.color('red')

        if self.winner == 'player':
            winner_name = str(player.character).upper()
        elif self.winner == 'foe':
            winner_name = str(enemy.character).upper()
        else:
            winner_name = 'Ninguém'

        if 1 < self.fight_anim_clock_count <= 8:

            if not end:
                self.winner_name_display = self.winner_name_object.render(f'{winner_name} VENCE!', True,
                                                                          winner_name_color)
                message_size = self.winner_name_display.get_size()

                screen.blit(self.winner_name_display, (SCREEN_WIDTH / 2 - message_size[0] / 2,
                                                       self.current_round_back_y))
            else:
                self.winner_name_display = self.winner_name_object.render('LUTA ENCERRADA!', True, fight_over_color)
                message_size = self.winner_name_display.get_size()

                screen.blit(self.winner_name_display, (SCREEN_WIDTH / 2 - message_size[0] / 2,
                                                       self.current_round_back_y))

        if self.fight_anim_clock_count >= 6:

            if not end:
                screen.blit(self.fight_round_fade, (self.fight_round_fade_x, 0))

                self.fight_round_fade_x += self.fight_round_fade_vel

                if self.fight_round_fade_x >= 0:
                    self.fight_round_fade_x = 0
            else:
                attacks = self.l_attack_types[:]
                heavy = self.h_attack_types[:]
                attacks.extend(heavy)

                if self.fight_anim_clock_count == 9 and self.fight_anim_clock == 0:
                    if self.winner == 'player':
                        p_attack_command = True
                        p_attack_kind = choice(attacks)
                        player.current_sprite = 0
                    else:
                        f_attack_kind = choice(attacks)
                        enemy.current_sprite = 0

    def display_hud(self):
        global BACKGROUND

        BACKGROUND = fight_background

        if not hide_fight_hud:
            life_color = design.color('dark green')
            life_shadow_color = design.color('dark red')
            life_bar_back = design.color('dark brown')

            energy_color = design.color('mid yellow')

            names_color = design.color('black')

            pygame.draw.rect(screen, life_bar_back, self.p_life_bar_back_rect)
            pygame.draw.rect(screen, life_bar_back, self.f_life_bar_back_rect)
            pygame.draw.rect(screen, life_bar_back, self.p_ult_bar_back_rect)
            pygame.draw.rect(screen, life_bar_back, self.f_ult_bar_back_rect)

            pygame.draw.rect(screen, life_shadow_color, ([self.p_life_shadow_x + self.p_life_bar_outline_pos[0],
                                                          self.p_life_bar_outline_pos[1] +
                                                          self.life_bar_outline_size[1] / 2],
                                                         [self.p_life_shadow, self.life_bar_outline_size[1] / 2 - 3]))

            pygame.draw.rect(screen, life_shadow_color, ([self.f_life_bar_outline_pos[0] +
                                                          self.f_life_bar_outline_rect[0],
                                                          self.f_life_bar_outline_pos[1] +
                                                          self.life_bar_outline_size[1] / 2],
                                                         [self.f_life_shadow, self.life_bar_outline_size[1] / 2 - 3]))

            pygame.draw.rect(screen, life_color, ([self.p_life_bar_outline_rect[0] + self.p_life_bar_outline_pos[0],
                                                   self.p_life_bar_outline_pos[1] + self.life_bar_outline_size[1] / 2],
                                                  [self.p_life_size, self.life_bar_outline_size[1] / 2 - 3]))

            pygame.draw.rect(screen, life_color, ([self.f_life_bar_outline_rect[0] + self.f_life_bar_outline_pos[0],
                                                   self.f_life_bar_outline_pos[1] + self.life_bar_outline_size[1] / 2],
                                                  [self.f_life_size, self.life_bar_outline_size[1] / 2 - 3]))

            if self.player_energy > 0:
                if self.player_energy >= self.energy_max:
                    self.player_energy = self.energy_max

                pygame.draw.rect(screen, energy_color, ([self.p_ult_bar_outline_rect[0] +
                                                         self.p_ult_bar_outline_pos[0] + 2,
                                                         self.p_ult_bar_outline_rect[1] +
                                                         self.p_ult_bar_outline_pos[1] + 2],
                                                        [self.energy_proportion * self.player_energy - 2,
                                                         self.p_ult_bar_outline_rect[3] - 2]))

            if self.foe_energy > 0:
                if self.foe_energy >= self.energy_max:
                    self.foe_energy = self.energy_max

                pygame.draw.rect(screen, energy_color, ([self.f_ult_bar_outline_rect[0] +
                                                         self.f_ult_bar_outline_pos[0] + 2,
                                                         self.f_ult_bar_outline_rect[1] +
                                                         self.f_ult_bar_outline_pos[1] + 2],
                                                        [self.energy_proportion * self.foe_energy - 2,
                                                         self.f_ult_bar_outline_rect[3] - 2]))

            screen.blit(self.p_life_bar_outline, self.p_life_bar_outline_pos)
            screen.blit(self.f_life_bar_outline, self.f_life_bar_outline_pos)

            screen.blit(self.p_ult_bar_outline, self.p_ult_bar_outline_pos)
            screen.blit(self.f_ult_bar_outline, self.f_ult_bar_outline_pos)

            self.player_name_display = self.player_name_object.render(player.character.upper(), True, names_color)
            self.foe_name_display = self.foe_name_object.render(enemy.character.upper(), True, names_color)

            screen.blit(self.player_name_display, (self.p_life_bar_outline_pos[0] + 20,
                                                   self.p_life_bar_outline_pos[1] + 1))
            screen.blit(self.foe_name_display, (SCREEN_WIDTH - 50 - self.foe_name_display.get_size()[0] - 20,
                                                self.f_life_bar_outline_pos[1] + 1))

            p_wins_char = 'O '
            f_wins_char = 'O '
            wins_color = design.color('red')

            self.player_wins_display = self.player_wins_object.render(p_wins_char * self.player_wins, True, wins_color)
            self.foe_wins_display = self.foe_wins_object.render(f_wins_char * self.foe_wins, False, wins_color)

            p_wins_pos = (self.p_life_bar_outline_pos[0],
                          self.p_life_bar_outline_pos[1] + self.p_life_bar_outline_rect[3] + 5)

            f_wins_pos = (self.f_life_bar_outline_pos[0] + self.f_life_bar_outline_rect[2]
                          - self.foe_wins_display.get_size()[0],
                          self.f_life_bar_outline_pos[1] + self.f_life_bar_outline_rect[3] + 5)

            screen.blit(self.player_wins_display, p_wins_pos)
            screen.blit(self.foe_wins_display, f_wins_pos)

        if not hide_fight_clock:
            if not pause_fight_clock:
                if self.fight_clock_count < 10:
                    time_displayed = f'0{self.fight_clock_count}'
                else:
                    time_displayed = f'{self.fight_clock_count}'
            else:
                time_displayed = '00'
            self.fight_time_display = self.fight_time_display_object.render(time_displayed, True,
                                                                            design.color('red'))
            screen.blit(self.fight_time_display, self.fight_time_pos)


class Ultimate(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.init = False
        self.activated = False
        self.changes = False
        self.end_ult = False

        self.ultimate_list = ultimates_sprites['Caipora'][1]

        self.ultimate_flash = ultimates_sprites['Caipora'][0]
        self.ultimate_flash_rect = self.ultimate_flash.get_rect()
        self.ultimate_flash_box = self.ultimate_flash.get_bounding_rect()
        self.ultimate_flash_x = 0
        self.ultimate_flash_y = 0
        self.ultimate_flash_vel = 23

        self.ultimate_flash_inverting = False
        self.ultimate_flash_inversion = False
        self.start_flash_inversion = False

        self.ultimate_display = self.ultimate_list[0]
        self.ultimate_display_rect = self.ultimate_display.get_rect()
        self.ultimate_display_box = self.ultimate_display.get_bounding_rect()
        self.ultimate_display_x = 0
        self.ultimate_display_y = 0
        self.ultimate_display_vel = 23

        self.p_ult_hit_validate = True
        self.f_ult_hit_validate = True

        self.ult_collided = False

        self.current_sprite = 0

        self.user = ''
        self.hide_user_player = False
        self.hide_user_foe = False

        self.ultimate_clock = 0
        self.ultimate_clock_counter = 0

        self.user_looking_right = True

        self.ult_command_clock = 0
        self.ult_command_clock_counter = 0

        self.p_ult_command_validate = False
        self.f_ult_command_validate = False
        self.ult_command_verifier = 0

        self.ult_sequence = ''
        self.ult_commands = database.get_ult_commands()
        self.ult_sequence_delay = 0.33

        self.reset_ult_system = False

    def ult_init(self, char, f_player, resize=1.0, not_right=False):

        if not self.changes:
            self.ultimate_flash = ultimates_sprites[char][0]
            self.ultimate_list = ultimates_sprites[char][1][:]

            if f_player:
                self.user = 'player'
            else:
                self.user = 'foe'

            rect_l = self.ultimate_list[0].get_rect()
            rect_f = self.ultimate_flash.get_rect()

            box_l = self.ultimate_list[0].get_bounding_rect()
            box_f = self.ultimate_flash.get_bounding_rect()

            if resize != 1.0:

                tools.set_size(self.ultimate_list, (int(rect_l[2] * resize), int(rect_l[3] * resize)))
                self.ultimate_flash = tools.set_size(self.ultimate_flash, (int(rect_f[2] * resize * 0.7),
                                                                           int(rect_f[3] * resize * 0.7)))

                rect_l = self.ultimate_list[0].get_rect()
                rect_f = self.ultimate_flash.get_rect()

                box_l = self.ultimate_list[0].get_bounding_rect()
                box_f = self.ultimate_flash.get_bounding_rect()

            if not_right:
                self.ultimate_flash = pygame.transform.flip(self.ultimate_flash, True, False)

                for index, sprite in enumerate(self.ultimate_list):
                    self.ultimate_list[index] = pygame.transform.flip(sprite, True, False)

            self.ultimate_display = self.ultimate_list[0]

            self.ultimate_flash_x = -rect_f[0] - box_f[2]
            self.ultimate_flash_y = SCREEN_HEIGHT - box_f[1] - box_f[3]

            self.ultimate_display_x = -rect_l[0] - box_l[2]
            self.ultimate_display_y = SCREEN_HEIGHT - box_l[1] - box_l[3] - 45

            self.ultimate_flash_box = box_f
            self.ultimate_flash_rect = rect_f

            self.ultimate_display_box = box_l
            self.ultimate_display_rect = rect_l

            self.user_looking_right = True

            if self.user == 'player' and not player.current_looking_right\
                    or self.user == 'foe' and not enemy.current_looking_right:

                self.ultimate_flash = pygame.transform.flip(self.ultimate_flash, True, False)

                for index, sprite in enumerate(self.ultimate_list):
                    self.ultimate_list[index] = pygame.transform.flip(sprite, True, False)

                self.user_looking_right = False

                self.ultimate_flash_x = SCREEN_WIDTH - rect_f[0]
                self.ultimate_display_x = SCREEN_WIDTH - rect_l[0]

            self.changes = True

        if self.user_looking_right:
            if self.ultimate_flash_x >= 0:
                self.ultimate_flash_x = 0
                self.start_flash_inversion = True
        else:
            if self.ultimate_flash_x <= SCREEN_WIDTH - self.ultimate_flash_box[2]:
                self.ultimate_flash_x = SCREEN_WIDTH - self.ultimate_flash_box[2]
                self.start_flash_inversion = True

        if self.start_flash_inversion:
            if self.ultimate_clock_counter == 3:
                self.ultimate_flash_inverting = True
                self.ultimate_flash_inversion = True

            elif not self.ultimate_flash_inverting:
                self.ultimate_flash_inversion = False

        if self.ultimate_flash_inversion:

            if self.user_looking_right and self.ultimate_flash_x <= -self.ultimate_flash_box[2]:
                self.ultimate_flash_x = -self.ultimate_flash_box[2]

            elif self.ultimate_flash_x >= SCREEN_WIDTH:
                self.ultimate_flash_x = SCREEN_WIDTH

            if self.ultimate_clock_counter >= 5:
                self.activated = True
                self.init = False

        screen.blit(self.ultimate_flash, (self.ultimate_flash_x, self.ultimate_flash_y))

        if not self.ultimate_flash_inversion:
            if self.user_looking_right:
                self.ultimate_flash_x += self.ultimate_flash_vel
            else:
                self.ultimate_flash_x -= self.ultimate_flash_vel
        else:
            if self.user_looking_right:
                self.ultimate_flash_x -= self.ultimate_flash_vel
            else:
                self.ultimate_flash_x += self.ultimate_flash_vel

    def ult_animation(self, repeat=True, ranged=True):
        global fight_system

        if ranged:
            if self.user_looking_right:
                if self.ultimate_display_x >= SCREEN_WIDTH:
                    self.ultimate_display_x = SCREEN_WIDTH
                    self.end_ult = True
            else:
                if self.ultimate_display_x <= -self.ultimate_display_box[2]:
                    self.ultimate_display_x = -self.ultimate_display_box[2]
                    self.end_ult = True

        if self.end_ult:
            self.activated = False
            fight_system.fight_happening = True

            if self.user == 'player':
                fight_system.player_energy = 0

            elif self.user == 'foe':
                fight_system.foe_energy = 0
                fight_bot.do_ultimate = False

            self.p_ult_command_validate = False
            self.f_ult_command_validate = False
            self.hide_user_player = False
            self.hide_user_foe = False

        if repeat:
            if self.current_sprite >= len(self.ultimate_list):
                self.current_sprite = 0
        else:
            if self.current_sprite >= len(self.ultimate_list):
                self.current_sprite = len(self.ultimate_list) - 1
                self.end_ult = True

        self.ultimate_display = self.ultimate_list[self.current_sprite]
        self.current_sprite += 1

        screen.blit(self.ultimate_display, (self.ultimate_display_x, self.ultimate_display_y))

        if ranged:
            if self.user_looking_right:
                self.ultimate_display_x += self.ultimate_display_vel
            else:
                self.ultimate_display_x -= self.ultimate_display_vel
        else:
            if self.user == 'player':
                self.ultimate_display_x = player.real_rect[0] - self.ultimate_display_box[0] - \
                                          self.ultimate_display_box[2] / 2
                if not self.end_ult:
                    self.hide_user_player = True
            else:
                self.ultimate_display_x = enemy.real_rect[0] - self.ultimate_flash_box[0] - \
                                          self.ultimate_display_box[2] / 2
                if not self.end_ult:
                    self.hide_user_foe = True

    def reset(self):

        self.ultimate_clock_counter = 0
        self.ultimate_clock = 0
        self.changes = False
        self.current_sprite = 0
        self.init = True
        self.activated = False
        self.ultimate_flash_inverting = False
        self.ultimate_flash_inversion = False
        self.start_flash_inversion = False
        self.end_ult = False

        self.user = ''

        self.p_ult_hit_validate = True
        self.f_ult_hit_validate = True

        self.ult_collided = False

        fight_system.player_being_hit = False
        fight_system.foe_being_hit = False

        self.reset_ult_system = True

    def validate_ult_command(self):
        global pressed_key

        self.ult_sequence = self.ult_commands[player.character]

        if self.ult_command_clock >= CLOCK_FPS / 3:
            self.ult_command_clock_counter += 1
            self.ult_command_clock = 0

        self.ult_command_clock += 1

        if self.ult_command_verifier == len(self.ult_sequence):
            if fight_system.player_energy >= fight_system.energy_max and fight_system.fight_happening:
                self.p_ult_command_validate = True
                self.reset_ult_system = False
                b_moves_sounds['ultimate'].play()

        if self.ult_command_clock_counter > self.ult_sequence_delay:
            pressed_key = ''
            self.ult_command_clock_counter = 0
            self.ult_command_clock = 0
            self.ult_command_verifier = 0

        if not self.ult_command_verifier == len(self.ult_sequence):
            if pressed_key == self.ult_sequence[self.ult_command_verifier]:
                self.ult_command_verifier += 1
                self.ult_command_clock_counter = 0
                self.ult_command_clock = 0

    def update(self):
        global p_attack_kind, f_attack_kind

        if self.user_looking_right:
            collision_point = self.ultimate_display_x + self.ultimate_display_box[2]
        else:
            collision_point = self.ultimate_display_x

        if self.activated:
            if self.user == 'player':
                if self.user_looking_right and collision_point >= enemy.real_rect[0] and not self.ult_collided or\
                        not self.user_looking_right and collision_point <= enemy.real_rect[0] + enemy.char_box[2] and\
                        not self.ult_collided:

                    fight_system.foe_being_hit = True
                    enemy.being_hit = True
                    p_attack_kind = 'ultimate'

                    self.p_ult_hit_validate = False
                    self.ult_collided = True
                else:
                    fight_system.foe_being_hit = False

            if self.user == 'foe':
                if self.user_looking_right and collision_point >= player.real_rect[0] and not self.ult_collided or\
                        not self.user_looking_right and collision_point <= player.real_rect[0] + player.char_box[2] and\
                        not self.ult_collided:

                    fight_system.player_being_hit = True
                    player.being_hit = True
                    f_attack_kind = 'ultimate'

                    self.f_ult_hit_validate = False
                    self.ult_collided = True
                else:
                    fight_system.player_being_hit = False

        if self.ultimate_clock >= CLOCK_FPS:
            self.ultimate_clock_counter += 1
            self.ultimate_clock = 0

        if self.ultimate_clock_counter >= 30:
            self.ultimate_clock_counter = 30

        self.ultimate_clock += 1

        if self.activated:
            self.ultimate_flash_rect = self.ultimate_flash.get_rect()
            self.ultimate_flash_box = self.ultimate_flash.get_bounding_rect()

            self.ultimate_display_rect = self.ultimate_display.get_rect()
            self.ultimate_display_box = self.ultimate_display.get_bounding_rect()

            self.ultimate_flash_y = SCREEN_HEIGHT - self.ultimate_flash_box[1] - self.ultimate_flash_box[3]
            self.ultimate_display_y = SCREEN_HEIGHT - self.ultimate_display_box[1] - self.ultimate_display_box[3] - 45


class FSMAI:

    def __init__(self, difficult):

        self.mode = ''
        self.difficult = difficult

        self.rage_multiplier = 1.5
        self._applied_rage = False

        self.hit_counter = 0

        self.had_action = False
        self.bot_delay = 0
        self.got_bot_delay = False
        self.right_distance = 10
        self.bot_is_close = False
        self.safe_distance = 300

        self.do_attack = False
        self.do_defend = False
        self.do_jump = False
        self.do_dash_right = False
        self.do_dash_left = False
        self.do_idle = False
        self.do_crouch = False
        self.do_walk_right = False
        self.do_walk_left = False
        self.do_ultimate = False

        self.tested_ultimate = False

        self.l_attacks = ['Straight Strike', 'Rising Strike', 'Low Pushed Hit']
        self.h_attacks = ['Quick Assault', 'Crescent Assault', 'Ground Ring Blow']

    def update(self):

        if player.current_looking_right and self.do_walk_right:
            self.do_walk_right = False
        if not player.current_looking_right and self.do_walk_left:
            self.do_walk_left = False

        if not player.is_dead and not enemy.is_dead:
            if not player.is_attacking:
                if self.difficult == 'normal':
                    self.mode = 'attack_normal'
                else:

                    if fight_system.foe_hp >= fight_system.f_hp_register * 0.4:
                        self.mode = 'attack_offensive'
                        self._applied_rage = False
                    else:
                        self.mode = 'attack_rage'

                        if not self._applied_rage:
                            fight_system.foe_atk *= self.rage_multiplier

                            self._applied_rage = True
            elif enemy.being_hit:
                if self.difficult == 'normal':
                    self.mode = 'defense_normal'
                else:

                    if fight_system.foe_hp >= fight_system.f_hp_register * 0.4:
                        self.mode = 'defense_applied'
                    else:
                        self.mode = 'defense_rage'
        else:
            self.mode = ''

    def activate_mode(self):

        if not enemy.is_dead and not player.is_dead:
            if len(self.mode) > 6 and self.mode[0:6] == 'attack':
                self.attack_mode()

            if len(self.mode) > 7 and self.mode[0:7] == 'defense':
                self.mode_defense()
            else:
                self.do_defend = False

    def attack_mode(self):
        global f_attack_kind

        if not self.got_bot_delay:

            if self.difficult == 'normal':
                self.bot_delay = fight_system.fight_clock_count + randint(1, 4)
                if self.bot_is_close:
                    self.bot_delay = fight_system.fight_clock_count + randint(0, 2)
            else:
                if not self.mode == 'attack_rage':
                    self.bot_delay = fight_system.fight_clock_count + randint(1, 3)
                else:
                    self.bot_delay = fight_system.fight_clock_count + randint(0, 1)
                if self.bot_is_close:
                    if not self.mode == 'attack_rage':
                        self.bot_delay = fight_system.fight_clock_count + randint(0, 1)

            self.got_bot_delay = True

        if not fight_system.fight_happening or game_paused:
            self.got_bot_delay = False

        if fight_system.fight_clock_count >= self.bot_delay:

            if not enemy.is_dead:
                if not self.tested_ultimate:
                    ult_chance = randint(1, 100)

                    if self.difficult == 'normal':
                        if ult_chance in range(1, 7) and fight_system.foe_energy >= fight_system.energy_max:
                            b_moves_sounds['ultimate'].play()
                            self.do_ultimate = True
                    else:
                        if not self.mode == 'attack_rage':
                            if ult_chance in range(1, 26) and fight_system.foe_energy >= fight_system.energy_max:

                                if enemy.character == 'Boitata':
                                    self.chase_player()
                                    if self.bot_is_close:
                                        b_moves_sounds['ultimate'].play()
                                        self.do_ultimate = True
                                else:
                                    b_moves_sounds['ultimate'].play()
                                    self.do_ultimate = True
                        else:
                            if ult_chance in range(1, 51) and fight_system.foe_energy >= fight_system.energy_max:

                                if enemy.character == 'Boitata':
                                    self.chase_player()
                                    if self.bot_is_close:
                                        b_moves_sounds['ultimate'].play()
                                        self.do_ultimate = True
                                else:
                                    b_moves_sounds['ultimate'].play()
                                    self.do_ultimate = True

                    self.tested_ultimate = True

            if not self.do_ultimate:
                self.chase_player()

                if self.bot_is_close:

                    if self.mode == 'attack_normal':
                        chance = randint(1, 100)

                        if chance in range(1, 61):
                            f_attack_kind = choice(self.l_attacks)
                        else:
                            f_attack_kind = choice(self.h_attacks)
                        self.had_action = True

                    elif self.mode == 'attack_offensive':
                        chance = randint(1, 100)

                        if chance in range(1, 31):
                            f_attack_kind = choice(self.l_attacks)
                        else:
                            f_attack_kind = choice(self.h_attacks)
                        self.had_action = True

                    else:
                        f_attack_kind = choice(self.h_attacks)
                        self.had_action = True

                    if self.had_action:
                        if not self.do_attack and fight_system.fight_happening:
                            if f_attack_kind in self.l_attacks:
                                b_moves_sounds['light'].play()
                            else:
                                b_moves_sounds['heavy'].play()
                            self.do_attack = True
                        self.got_bot_delay = False
                        self.tested_ultimate = False

                        self.had_action = False

    def chase_player(self):

        if enemy.current_looking_right:
            if player.real_rect[0] > enemy.real_rect[0] + enemy.char_box[2] + self.right_distance:
                self.do_walk_right = True
                self.bot_is_close = False

                if player.real_rect[0] > enemy.real_rect[0] + enemy.char_box[2] + self.safe_distance:

                    if self.mode == 'attack_normal':
                        if not self.do_dash_right:
                            chance = randint(1, 100)

                            if chance in range(1, 9):
                                self.do_dash_right = True
                    else:
                        if not self.do_dash_right:
                            chance = randint(1, 100)

                            if chance in range(1, 41):
                                self.do_dash_right = True
            else:
                self.do_walk_right = False
                self.do_dash_right = False
                self.bot_is_close = True

        else:
            if player.real_rect[0] + player.char_box[2] < enemy.real_rect[0] - self.right_distance:
                self.do_walk_left = True
                self.bot_is_close = False

                if player.real_rect[0] + player.char_box[2] < enemy.real_rect[0] - self.safe_distance:

                    if self.mode == 'attack_normal':
                        if not self.do_dash_left:
                            chance = randint(1, 100)

                            if chance in range(1, 9):
                                self.do_dash_left = True
                    else:
                        if not self.do_dash_right:
                            chance = randint(1, 100)

                            if chance in range(1, 41):
                                self.do_dash_left = True
            else:
                self.do_walk_left = False
                self.do_dash_left = False
                self.bot_is_close = True

    def mode_defense(self):

        if self.mode == 'defense_normal':

            if p_consecutive_hits < 5 and not fight_system.foe_hp <= fight_system.f_hp_register * 0.3:
                self.do_defend = True

            else:
                self.do_defend = False
                self.flee()

        else:

            if p_consecutive_hits < 2 and not fight_system.foe_hp <= fight_system.f_hp_register * 0.6:
                self.do_defend = True

            else:
                self.do_defend = False
                self.flee()

    def flee(self):

        if enemy.current_looking_right:
            if player.real_rect[0] <= enemy.real_rect[0] + enemy.char_box[2] + self.safe_distance:
                if not foe_on_limit == 'left':
                    self.do_walk_left = True

                    if enemy.being_hit and not self.do_dash_left:
                        chance = randint(1, 100)

                        if self.mode == 'defense_normal':
                            if chance in range(1, 21):
                                self.do_dash_left = True
                        elif self.mode == 'defense_applied':
                            if chance in range(1, 41):
                                self.do_dash_left = True
                        else:
                            if chance in range(1, 91):
                                self.do_dash_left = True

                else:
                    self.do_walk_right = True

                    if enemy.being_hit and not self.do_dash_right:
                        chance = randint(1, 100)

                        if self.mode == 'defense_normal':
                            if chance in range(1, 21):
                                self.do_dash_right = True
                        elif self.mode == 'defense_applied':
                            if chance in range(1, 41):
                                self.do_dash_right = True
                        else:
                            if chance in range(1, 91):
                                self.do_dash_right = True
            else:
                self.do_walk_left = False
                self.do_dash_left = False

        else:
            if player.real_rect[0] + player.char_box[2] >= enemy.real_rect[0] - self.safe_distance:
                if not foe_on_limit == 'right':
                    self.do_walk_right = True

                    if enemy.being_hit and not self.do_dash_right:
                        chance = randint(1, 100)

                        if self.mode == 'defense_normal':
                            if chance in range(1, 21):
                                self.do_dash_right = True
                        elif self.mode == 'defense_applied':
                            if chance in range(1, 41):
                                self.do_dash_right = True
                        else:
                            if chance in range(1, 91):
                                self.do_dash_right = True
                else:
                    self.do_walk_left = True

                    if enemy.being_hit and not self.do_dash_left:
                        chance = randint(1, 100)

                        if self.mode == 'defense_normal':
                            if chance in range(1, 21):
                                self.do_dash_left = True
                        elif self.mode == 'defense_applied':
                            if chance in range(1, 41):
                                self.do_dash_left = True
                        else:
                            if chance in range(1, 91):
                                self.do_dash_left = True
            else:
                self.do_walk_right = False
                self.do_dash_right = False


class Character(pygame.sprite.Sprite):

    def __init__(self, character, resize=1.0, looking_right=True, is_player=True):
        pygame.sprite.Sprite.__init__(self)

        self.character = character
        self.is_player = is_player

        self.standing_sprites = character_sprites[character][0].copy()
        self.walking_sprites = character_sprites[character][1].copy()
        self.jump_sprites = character_sprites[character][2].copy()
        self.dash_sprites = character_sprites[character][3].copy()
        self.defense_sprites = character_sprites[character][4].copy()
        self.dead_sprites = character_sprites[character][5].copy()
        self.hit_sprites = character_sprites[character][6].copy()
        self.crouch_sprites = character_sprites[character][7].copy()

        self.l_attack_sprites = []
        self.h_attack_sprites = []

        for s_list in b_moves_sprites[character]['Light Attacks']:
            self.l_attack_sprites.append(s_list[:])

        for s_list in b_moves_sprites[character]['Heavy Attacks']:
            self.h_attack_sprites.append(s_list[:])

        self.all_sprites = [self.standing_sprites, self.walking_sprites, self.jump_sprites,
                            self.dash_sprites, self.defense_sprites, self.dead_sprites,
                            self.hit_sprites, self.crouch_sprites]

        for index in enumerate(self.l_attack_sprites):
            self.all_sprites.append(self.l_attack_sprites[index[0]])

        for index in enumerate(self.h_attack_sprites):
            self.all_sprites.append(self.h_attack_sprites[index[0]])

        if not looking_right:

            for sprite_list in self.all_sprites:
                for index, sprite in enumerate(sprite_list):
                    sprite_list[index] = pygame.transform.flip(sprite, True, False)

        self.image = self.standing_sprites[0]
        self.current_sprite = 0

        self.rect = self.image.get_rect()

        if resize != 1.0:
            self.image = tools.set_size(self.image, (int(self.rect[2] * resize), int(self.rect[3] * resize)))
            tools.set_size(self.all_sprites, (int(self.rect[2] * resize), int(self.rect[3] * resize)))

        self.rect = self.image.get_rect()

        self.char_box = tools.get_hit_box_coords(self)
        self.first_char_box = self.char_box

        self.real_rect = [(self.rect[0] + self.char_box[0]), (self.rect[1] + self.char_box[1])]

        self.mask = pygame.mask.from_surface(self.image)

        self.is_moving = False
        self.is_moving_backwards = False
        self.dont_move = False
        self.being_pushed = False

        self.is_crouching = False
        self.just_crouched = False
        self.is_looking_up = False

        self.is_jumping = False
        self.jump_count = JUMP_HEIGHT

        self.look_right = True
        self.current_looking_right = True

        self.dash_activate = False
        self.is_dashing = 0
        self.dash_time = 0
        self.dashing_to_right = True

        self.is_attacking = False
        self.attack_verifier = 0
        self.attack_time = 0
        self.attack_pre_key = ''
        self.l_attack_types = ['Straight Strike', 'Rising Strike', 'Low Pushed Hit']
        self.h_attack_types = ['Quick Assault', 'Crescent Assault', 'Ground Ring Blow']

        self.is_defending = False

        self.is_dead = False
        self.being_hit = False

        self.break_commands = False

    def position(self, in_right_side=False):

        if in_right_side:
            self.rect[0] = SCREEN_WIDTH - self.real_rect[0] - self.char_box[2]
        else:
            self.rect[0] = 0 - self.real_rect[0]

        self.rect[1] = GROUND_LIMIT - self.real_rect[1] - self.char_box[3]

    def move(self, right=True):

        if not self.break_commands:
            if right:
                self.rect[0] += PLAYER_SPEED

            else:
                self.rect[0] -= PLAYER_SPEED

    def jump(self):

        if not self.break_commands:
            if self.jump_count == JUMP_HEIGHT:
                self.is_jumping = True

            if self.jump_count >= -JUMP_HEIGHT:
                negative = 1
                if self.jump_count < 0:
                    negative = -1

                if negative > 0:
                    if self.current_sprite >= 10:
                        self.rect[1] -= int((self.jump_count ** 2) * 0.5 * negative)
                        self.jump_count -= 1
                        if self.current_sprite >= 14:
                            self.current_sprite = 14
                else:
                    self.rect[1] -= int((self.jump_count ** 2) * 0.5 * negative)
                    self.jump_count -= 1
            else:
                self.is_jumping = False
                self.jump_count = JUMP_HEIGHT

    def crouch(self):

        if not self.is_dead and not self.is_jumping and not self.is_attacking:
            tools.animate_char(self, self.crouch_sprites, break_last=True)

            if self.current_sprite == len(self.crouch_sprites) - 1:
                self.just_crouched = False

            self.is_crouching = True
            self.break_commands = True

    def dash(self):

        if not self.break_commands:
            self.is_dashing += DASH_SPEED

            if not self.dashing_to_right:
                self.rect[0] -= self.is_dashing
            else:
                self.rect[0] += self.is_dashing

            if self.is_dashing >= DASH_RANGE:
                self.is_dashing = 0
                self.dash_activate = False

                if not self.is_player:
                    self.being_hit = False
                    fight_bot.do_dash_right = False
                    fight_bot.do_dash_left = False

    def dash_clock(self):

        if self.dash_time >= 50:
            self.dash_time = 50

        else:
            self.dash_time += 1

    def light_attack(self):

        if not self.is_dead:
            if self.is_player:
                attack_kind = p_attack_kind
                fight_t.char_attack_control(self, attack_kind, light=True)

            else:
                attack_kind = f_attack_kind
                attacked = fight_t.char_attack_control(self, attack_kind, light=True, is_player=False)

                if attacked:
                    fight_bot.do_attack = False

    def heavy_attack(self):

        if not self.is_dead:
            if self.is_player:
                attack_kind = p_attack_kind
                fight_t.char_attack_control(self, attack_kind, light=False)

            else:
                attack_kind = f_attack_kind
                attacked = fight_t.char_attack_control(self, attack_kind, light=False, is_player=False)

                if attacked:
                    fight_bot.do_attack = False

    def defense(self):

        if not self.break_commands and not self.is_jumping and not self.is_attacking:
            self.is_defending = True
            self.being_hit = False

            if self.is_player:
                tools.animate_char(self, self.defense_sprites, break_last=True)
            else:
                self.image = self.defense_sprites[-1]

            self.break_commands = True

    def die(self):

        self.is_dead = True
        self.break_commands = True

        tools.animate_char(self, self.dead_sprites, break_last=True)

    def update(self):

        if self.current_looking_right:
            self.char_box = tools.get_hit_box_coords(self, False)

        else:
            self.char_box = tools.get_hit_box_coords(self, True)

        self.real_rect = [(self.rect[0] + self.char_box[0]), (self.rect[1] + self.char_box[1])]
        self.mask = pygame.mask.from_surface(self.image)

        if self.is_dead:
            self.break_commands = True

    def update_animation(self):

        if not self.break_commands:
            if self.is_dashing:
                tools.animate_char(self, self.dash_sprites)
            elif self.is_jumping and not self.being_hit:
                tools.animate_char(self, self.jump_sprites)

            else:
                if not self.is_defending:
                    if self.is_moving:

                        if self.is_moving_backwards:
                            tools.animate_char(self, self.walking_sprites, reverse=True)
                        else:
                            tools.animate_char(self, self.walking_sprites)

                    elif self.being_hit:
                        tools.animate_char(self, self.hit_sprites)

                        if self.current_sprite >= len(self.hit_sprites):
                            self.being_hit = False
                        else:
                            self.image.fill(design.color('red'), special_flags=BLEND_RGBA_MIN)

                    elif not self.is_attacking:
                        tools.animate_char(self, self.standing_sprites)


main = MainSystem()
menu = MenuSystem()

player = enemy = fight_system = ultimate_system = fight_bot = 0


def draw_on_screen():
    global foe_on_limit

    if not fight_system_started:
        screen.blit(BACKGROUND, (0, 0))

    if main.mode_intro:
        main.get_scene_clock()
        main.intro()

    if main.story_intro:
        main.get_scene_clock()
        main.intro(story=True)

    if main.mode_story and not main.mode_fight:
        main.get_scene_clock()
        main.cutscene()

    if main.mode_menu:
        menu.display_menu()

    if main.mode_fight and fight_system_started:
        global fight_background_x

        screen.blit(BACKGROUND, (fight_background_x, 0))
        fight_system.display_hud()

        if mirrored_foe and not enemy.being_hit:
            enemy.image.fill(design.color('mid blue'), special_flags=BLEND_RGBA_MIN)

        if fight_system.fight_happening:

            if player.real_rect[0] <= 0 and player.is_moving_backwards:
                if fight_background_x >= 0:
                    fight_background_x = 0
                else:
                    fight_background_x += SCREEN_SCROLL_VEL
                    enemy.rect[0] += SCREEN_SCROLL_VEL

            elif player.real_rect[0] + player.char_box[2] + 20 >= SCREEN_DIMENSION[0] and player.is_moving_backwards:
                if fight_background_x <= -fight_background_add_width:
                    fight_background_x = -fight_background_add_width
                else:
                    fight_background_x -= SCREEN_SCROLL_VEL
                    enemy.rect[0] -= SCREEN_SCROLL_VEL

        if fight_system.fight_happening or fight_system.fight_pause or fight_system.fight_start or\
                ultimate_system.activated or ultimate_system.init:

            enemy.update()
            player.update()

            tools.activate_collision(player, enemy, PLAYER_SPEED)

            if not player.is_dead:
                tools.set_focus(player, enemy, player.all_sprites)
            tools.set_in_screen(player, SCREEN_DIMENSION)

            if not enemy.is_dead:
                tools.set_focus(enemy, player, enemy.all_sprites)
            foe_on_limit = tools.set_in_screen(enemy, SCREEN_DIMENSION, True, fight_background_x, fight_background_size)

            enemy_group.update()
            player_group.update()

            enemy.update_animation()
            player.update_animation()

            if not ultimate_system.hide_user_foe:
                enemy_group.draw(screen)
            if not ultimate_system.hide_user_player:
                player_group.draw(screen)

            if ultimate_system.activated:
                if ultimate_system.user == 'player' and player.character == 'Caipora' or ultimate_system.user == 'foe'\
                        and enemy.character == 'Caipora':

                    ultimate_system.ult_animation(repeat=True, ranged=True)

                elif ultimate_system.user == 'player' and player.character == 'Boitata' or\
                        ultimate_system.user == 'foe' and enemy.character == 'Boitata':

                    ultimate_system.ult_animation(repeat=False, ranged=False)

            screen.blit(fight_background_front, (fight_background_x, SCREEN_HEIGHT - fight_background_front_height))

            if ultimate_system.p_ult_command_validate:

                if not ultimate_system.reset_ult_system:
                    ultimate_system.reset()

                player.is_moving = False
                enemy.is_moving = False
                player.is_attacking = False
                enemy.is_attacking = False

                ultimate_system.ult_init(player.character, f_player=True, resize=2, not_right=True)
                fight_system.fight_happening = False

            if ultimate_system.f_ult_command_validate and not ultimate_system.p_ult_command_validate:

                if not ultimate_system.reset_ult_system:
                    ultimate_system.reset()

                player.is_moving = False
                enemy.is_moving = False
                player.is_attacking = False
                enemy.is_attacking = False

                ultimate_system.ult_init(enemy.character, f_player=False, resize=2, not_right=True)
                fight_system.fight_happening = False

            if game_paused:
                main.pause_game()

        if fight_system.fight_pause and fight_system.winner == '' or fight_system.fight_start \
                and not fight_system.fight_over:
            fight_system.starting_round_animation()

        elif fight_system.fight_pause and not fight_system.fight_over:
            fight_system.ending_round_animation(end=False)
        elif fight_system.fight_over:
            fight_system.ending_round_animation(end=True)


# main loop_____________________________________________________________________________________________________________

playing = True
while playing:

    CLOCK.tick(CLOCK_FPS)

    # rules calculating_________________________________________________________________________________________________

    if start_fight_system and not fight_system_started:
        from random import choice

        player = Character(p_current_char, looking_right=False, is_player=True)

        enemy = Character(f_current_char, looking_right=False, is_player=False)
        fight_bot = FSMAI(difficult=fight_difficult)

        if player.character == enemy.character:
            mirrored_foe = True
        else:
            mirrored_foe = False

        player_group = pygame.sprite.Group(player)
        enemy_group = pygame.sprite.Group(enemy)

        fight_system = FightSystem(player, enemy)
        ultimate_system = Ultimate()

        player.position(in_right_side=False)
        enemy.position(in_right_side=True)

        player_saved_position = player.rect[:]
        foe_saved_position = enemy.rect[:]

        if not main.mode_story:
            fight_background = choice(fight_background_list)
        else:
            fight_background = fight_background_list[current_saved_level - 1]
            pause_fight_clock = False

        fight_background_front = fight_background_front_list[fight_background_list.index(fight_background)]

        fight_background_size = fight_background.get_size()
        fight_background_front_height = 550

        fight_background_front = tools.set_size(fight_background_front, (fight_background_size[0],
                                                                         SCREEN_HEIGHT - SCREEN_HEIGHT +
                                                                         fight_background_front_height))
        fight_background_front = pygame.transform.flip(fight_background_front, True, False)
        fight_background_x = -fight_background_add_width / 2

        start_this_fade = False

        fight_system.fight_pause = True

        start_fight_system = False
        fight_system_started = True

    main.update()

    if client is not None:
        if not mark_sent:
            if andura_mark[1] != '':
                try:
                    client.send(andura_mark[1])
                except Exception as e:
                    print(e)
                else:
                    mark_sent = True
                    receive_marks = True

        if receive_marks:
            try:
                other_marks.clear()
                their_mark = client.receive()

                if their_mark.find(' ') != -1:
                    their_mark = their_mark.split(' ')

                for m in their_mark:
                    other_marks.append(m)

            except Exception as e:
                print(e)
            else:
                receive_marks = False

    if main.mode_menu:
        menu.update()

    elif main.mode_fight and fight_system_started and not game_paused:

        if fight_system.fight_pause or fight_system.fight_start:
            fight_system.change_rounds()

        fight_system.update()
        fight_system.update_rules()
        fight_system.get_fight_clock()
        fight_system.bugs_fix(player, enemy)

        if not enemy.is_dead:
            fight_bot.update()
            fight_bot.activate_mode()

        if not player.is_dead and not enemy.is_dead:
            ultimate_system.update()

        if fight_system.fight_happening:
            ultimate_system.validate_ult_command()

        if fight_system.player_is_dead:
            if not player.is_dead:
                player.current_sprite = 0
            player.die()
        elif fight_system.foe_is_dead:
            if not enemy.is_dead:
                enemy.current_sprite = 0
            enemy.die()

    # draw on screen____________________________________________________________________________________________________

    draw_on_screen()

    # events control____________________________________________________________________________________________________

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False

        if main.mode_menu:
            if menu.andura_user_writing:

                if event.type == pygame.KEYDOWN:

                    if not len(menu.andura_mark_txt) > 6:
                        for key, value, in menu.letters.items():
                            if event.key == key:
                                menu.andura_mark_txt.append(value)

                    if not len(menu.andura_mark_txt) == 0:
                        if event.key == pygame.K_BACKSPACE:
                            menu.andura_mark_txt.pop()

                        elif event.key == pygame.K_SPACE:
                            menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                            menu.play_sound.play()
                            menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                            andura_mark[1] = ''.join(menu.andura_mark_txt)

                            if andura_mark[0] == 0:
                                andura_mark[0] = 1
                            pickle_dump(andura_mark, open('andura-mark.dat', 'wb'))

                            mark_sent = False
                            menu.andura_write_mode = False
                            menu.andura_user_writing = False
                            menu.andura_mark_txt.clear()

        if main.mode_menu or game_paused:

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_left_c = pygame.mouse.get_pressed()[0]
                mouse_right_c = pygame.mouse.get_pressed()[2]

                if mouse_left_c == 1:

                    if game_paused:
                        if main.mouse_on_menu:
                            menu.play_sound.play()
                            menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                            main.mode_fight = False
                            main.mode_story = False
                            game_paused = False
                            fight_system_started = False
                            main.playing_music = False

                            main.mode_menu = True
                            menu.menu = True

                    if menu.menu:
                        fight_system_started = False
                        menu.chars_selected = 0

                        if menu.mouse_on['exit']:
                            menu.play_sound.play()
                            playing = False

                        elif menu.mouse_on['f_fight']:
                            menu.play_sound.play()
                            main.playing_music = False
                            menu.menu = False
                            menu.char_selection = True

                        elif menu.mouse_on['new_game'] or menu.mouse_on['load_game']:
                            menu.play_sound.play()
                            menu.menu = False
                            menu.saves = True

                            if menu.mouse_on['new_game']:
                                menu.play_sound.play()
                                main.new_game_mode = True
                            else:
                                main.load_game_mode = True

                        elif menu.mouse_on['andura']:
                            menu.play_sound.play()
                            main.playing_music = False

                            if andura_mark[1] != '':
                                mark_sent = False

                            menu.menu = False
                            menu.andura = True

                        elif menu.mouse_on['tutorial']:
                            menu.play_sound.play()
                            main.playing_music = False
                            menu.menu = False
                            menu.tutorial = True

                    elif menu.saves:

                        if menu.mouse_on['back']:
                            menu.play_sound.play()
                            menu.saves = False
                            menu.menu = True

                            main.new_game_mode = False
                            main.load_game_mode = False

                        if main.new_game_mode:

                            if menu.mouse_on['accept']:

                                if current_save == 1:
                                    menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                                    menu.play_sound.play()
                                    menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                                    pickle_dump(current_saved_level, open('save_1.dat', 'wb'))

                                elif current_save == 2:
                                    menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                                    menu.play_sound.play()
                                    menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                                    pickle_dump(current_saved_level, open('save_2.dat', 'wb'))

                                if current_save == 1 or current_save == 2:
                                    current_saved_level = 1
                                    menu.saves = False
                                    main.mode_menu = False
                                    main.story_intro = True
                                    main.new_game_mode = False
                                    main.load_game_mode = False
                                    main.playing_music = False

                            if menu.mouse_on['save_1']:
                                menu.play_sound.play()
                                pygame.draw.rect(screen, design.color('yellow'), menu.save_square_1['Rect'])
                                current_save = 1

                            elif menu.mouse_on['save_2']:
                                menu.play_sound.play()
                                pygame.draw.rect(screen, design.color('yellow'), menu.save_square_2['Rect'])
                                current_save = 2
                            else:
                                current_save = 0

                        else:

                            if menu.mouse_on['accept']:

                                if current_save == 1:
                                    try:
                                        current_saved_level = pickle_load(open('save_1.dat', 'rb'))
                                        menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                                        menu.play_sound.play()
                                        menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                                    except FileNotFoundError:
                                        current_save = 0

                                elif current_save == 2:
                                    try:
                                        current_saved_level = pickle_load(open('save_2.dat', 'rb'))
                                        menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                                        menu.play_sound.play()
                                        menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                                    except FileNotFoundError:
                                        current_save = 0

                                if current_save == 1 or current_save == 2:
                                    menu.saves = False
                                    main.mode_menu = False
                                    main.mode_story = True
                                    main.new_game_mode = False
                                    main.load_game_mode = False
                                    main.playing_music = False

                            if menu.mouse_on['save_1']:
                                menu.play_sound.play()
                                pygame.draw.rect(screen, design.color('yellow'), menu.save_square_1['Rect'])
                                current_save = 1

                            elif menu.mouse_on['save_2']:
                                menu.play_sound.play()
                                pygame.draw.rect(screen, design.color('yellow'), menu.save_square_2['Rect'])
                                current_save = 2
                            else:
                                current_save = 0

                    elif menu.char_selection:

                        if menu.chars_selected == 0:
                            menu.player_selected = False
                            menu.foe_selected = False

                        elif menu.chars_selected == 1:
                            menu.foe_selected = False
                            menu.player_selected = True

                        else:
                            menu.player_selected = True
                            menu.foe_selected = True

                        if menu.mouse_on['back']:
                            menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                            menu.play_sound.play()
                            if menu.chars_selected > 0:
                                menu.chars_selected -= 1
                                if menu.chars_selected == 0:
                                    f_current_char = ''
                            else:
                                menu.char_selection = False
                                menu.menu = True
                                main.playing_music = False

                        elif menu.mouse_on['pause_clock']:
                            menu.play_sound.play()
                            if not pause_fight_clock:
                                pause_fight_clock = True
                            else:
                                pause_fight_clock = False

                        elif menu.mouse_on['difficult']:
                            menu.play_sound.play()
                            if fight_difficult == 'normal':
                                fight_difficult = 'hard'
                            else:
                                fight_difficult = 'normal'

                        if menu.mouse_on['caipora']:
                            char_choice = 'Caipora'
                            menu.play_sound.play()
                            pygame.draw.rect(screen, design.color('red'), menu.caipora_button_rect)
                        elif menu.mouse_on['boitata']:
                            char_choice = 'Boitata'
                            menu.play_sound.play()
                            pygame.draw.rect(screen, design.color('red'), menu.boitata_button_rect)

                        if not menu.player_selected:
                            p_current_char = char_choice

                        if not menu.foe_selected and menu.player_selected:
                            f_current_char = char_choice

                        if menu.mouse_on['confirm']:
                            if p_current_char != '' and not menu.player_selected:
                                menu.play_sound.play()
                                menu.chars_selected += 1

                            elif f_current_char != '' and not menu.foe_selected:
                                menu.play_sound.play()
                                menu.chars_selected += 1

                            elif menu.chars_selected == 2:
                                menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                                menu.play_sound.play()

                                start_fight_system = True

                                main.mode_menu = False
                                main.mode_fight = True
                                main.playing_music = False

                                menu.char_selection = False

                    elif menu.andura:

                        if menu.andura_write_mode:
                            if not menu.mouse_on['writing']:
                                menu.andura_write_mode = False
                                menu.andura_user_writing = False
                                menu.andura_mark_txt.clear()
                            else:
                                menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                                menu.play_sound.play()
                                menu.andura_user_writing = True

                        if menu.mouse_on['back']:
                            menu.play_sound = pygame.mixer.Sound(menu.sounds['click'])
                            menu.play_sound.play()

                            main.playing_music = False
                            menu.andura = False
                            menu.menu = True

                        elif menu.mouse_on['yes_andura']:
                            menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                            menu.play_sound.play()

                            menu.andura_write_mode = True

                        elif menu.mouse_on['no_andura']:
                            menu.play_sound = pygame.mixer.Sound(menu.sounds['confirm_fight'])
                            menu.play_sound.play()

                    elif menu.tutorial:

                        if menu.mouse_on['back']:
                            menu.play_sound.play()

                            if menu.tutorial_slide <= 1:
                                main.playing_music = False
                                menu.tutorial = False
                                menu.menu = True
                            else:
                                menu.tutorial_slide -= 1

                        elif menu.mouse_on['next']:

                            if menu.tutorial_slide < 4:
                                menu.play_sound.play()
                                menu.tutorial_slide += 1

        if main.mode_fight and fight_system_started:

            if fight_system.fight_happening:
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        if not game_paused:
                            game_paused = True
                        else:
                            game_paused = False

                    if not game_paused:
                        if event.key == pygame.K_SPACE and not player.is_jumping and not player.is_attacking \
                                and not player.break_commands:
                            jump_command = True
                            player.current_sprite = 0

                        if not player.break_commands and not player.is_jumping and not player.being_hit\
                                and not player.is_attacking:
                            if event.key == pygame.K_s or event.key == pygame.K_w:
                                player.current_sprite = 0
                                if event.key == pygame.K_s:
                                    player.just_crouched = True

                        if event.key == pygame.K_l and not player.is_jumping and not player.is_moving \
                                and not player.is_attacking and not player.being_hit:
                            p_attack_command = True
                            b_moves_sounds['light'].play()

                            if player.is_crouching:
                                p_attack_kind = 'Low Pushed Hit'
                            elif player.is_looking_up:
                                player.is_defending = False
                                p_attack_kind = 'Rising Strike'
                            else:
                                p_attack_kind = 'Straight Strike'

                        if event.key == pygame.K_k and not player.is_jumping and not player.is_moving \
                                and not player.is_attacking and not player.being_hit:
                            p_attack_command = True
                            b_moves_sounds['heavy'].play()

                            if player.is_crouching:
                                p_attack_kind = 'Ground Ring Blow'
                            elif player.is_looking_up:
                                player.is_defending = False
                                p_attack_kind = 'Crescent Assault'
                            else:
                                p_attack_kind = 'Quick Assault'

                        if (event.key == pygame.K_d or event.key == pygame.K_a) and 8 > player.dash_time > 2:
                            player.dash_activate = True

                            if not player.is_jumping:
                                player.current_sprite = 0

                        if event.key == pygame.K_d:
                            player.dash_time = 0
                            player.dashing_to_right = True
                            pressed_key = 'd'

                        if event.key == pygame.K_a:
                            player.dash_time = 0
                            player.dashing_to_right = False
                            pressed_key = 'a'

                        if event.key == pygame.K_s:
                            pressed_key = 's'
                        if event.key == pygame.K_w:
                            pressed_key = 'w'
                        if event.key == pygame.K_k:
                            pressed_key = 'k'
                        if event.key == pygame.K_l:
                            pressed_key = 'l'

    if main.mode_fight and fight_system_started:

        if fight_system.fight_happening and not game_paused:

            command = pygame.key.get_pressed()

            if command[K_d] and not player.is_attacking and not player.being_hit:

                if not player.current_looking_right:
                    player.is_moving_backwards = True
                    player.dont_move = False
                else:
                    player.is_moving_backwards = False

                    if not enemy.is_crouching and not enemy.is_looking_up:
                        player.dont_move = False

                if not player.dont_move:
                    player.move(right=True)
                    player.is_moving = True

            elif command[K_a] and not player.is_attacking and not player.being_hit:

                if player.current_looking_right:
                    player.is_moving_backwards = True
                    player.dont_move = False
                else:
                    player.is_moving_backwards = False

                    if not enemy.is_crouching and not enemy.is_looking_up:
                        player.dont_move = False

                if not player.dont_move:
                    player.move(right=False)
                    player.is_moving = True

            elif not player.being_pushed:
                player.is_moving = False
                player.is_moving_backwards = False

            if command[K_s] and not player.being_hit:
                if not player.is_attacking and not player.just_crouched and not player.is_jumping\
                        and not player.is_dead:
                    player.current_sprite = len(player.crouch_sprites) - 2
                player.crouch()

            else:
                player.is_crouching = False
                player.break_commands = False

            if command[K_w] and not player.is_dead:
                player.defense()
                player.is_looking_up = True

            else:
                player.is_defending = False
                player.is_looking_up = False

            if fight_bot.do_defend:
                enemy.defense()
                enemy.is_looking_up = True

            else:
                enemy.is_defending = False
                enemy.is_looking_up = False
                enemy.break_commands = False

            if fight_bot.do_walk_right and not enemy.is_attacking and not enemy.being_hit:

                if not enemy.current_looking_right:
                    enemy.is_moving_backwards = True
                    enemy.dont_move = False
                else:
                    enemy.is_moving_backwards = False

                    if not player.is_crouching and not player.is_looking_up:
                        enemy.dont_move = False

                if not enemy.dont_move:
                    enemy.move(right=True)
                    enemy.is_moving = True

            elif fight_bot.do_walk_left and not enemy.is_attacking and not enemy.being_hit:

                if enemy.current_looking_right:
                    enemy.is_moving_backwards = True
                    enemy.dont_move = False
                else:
                    enemy.is_moving_backwards = False

                    if not player.is_crouching and not player.is_looking_up:
                        enemy.dont_move = False

                if not enemy.dont_move:
                    enemy.move(right=False)
                    enemy.is_moving = True

            elif not enemy.being_pushed:
                enemy.is_moving = False
                enemy.is_moving_backwards = False

        if not game_paused:
            if player.dash_activate:
                player.dash()

            player.dash_clock()

            if fight_bot.do_dash_right:
                enemy.dash()
                enemy.dashing_to_right = True

            elif fight_bot.do_dash_left:
                enemy.dash()
                enemy.dashing_to_right = False
            else:
                enemy.is_dashing = False

            if jump_command:
                player.jump()
                if not player.is_jumping:
                    jump_command = False

            if p_attack_command and p_attack_kind in player.l_attack_types:
                player.light_attack()
            elif p_attack_command and p_attack_kind in player.h_attack_types:
                player.heavy_attack()

            if not player.is_attacking:
                p_attack_command = False
                p_attack_kind = ''

            if fight_bot.do_attack and not fight_bot.do_defend and f_attack_kind in enemy.l_attack_types\
                    and not enemy.being_hit:
                enemy.light_attack()
            if fight_bot.do_attack and not fight_bot.do_defend and f_attack_kind in enemy.h_attack_types\
                    and not enemy.being_hit:
                enemy.heavy_attack()

            if not enemy.is_attacking:
                f_attack_kind = ''

            if fight_bot.do_ultimate and not enemy.is_dead:
                if not ultimate_system.f_ult_command_validate:
                    ultimate_system.reset_ult_system = False

                ultimate_system.f_ult_command_validate = True

    pygame.display.update()
pygame.quit()

resources_paths = compression.get_file_paths('paca-paua')
compression.compress_dir(resources_paths, 'paca-paua-compressed', 'paca-paua')
