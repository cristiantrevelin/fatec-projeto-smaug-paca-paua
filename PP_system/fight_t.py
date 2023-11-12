import pygame
from PP_system import tools, database

pygame.init()


def char_attack_control(char, attack_k, light=True, is_player=True):
    """
    > Controla a ativação das animações de ataque básico de um objeto de classe Character.

    :param char: Objeto de classe Character.
    :param attack_k: A variável global que controla o comando de ataque deste char.
    :param light: True para controlar os light attacks, False para os heavy attacks.
    :return: Nada.
    """

    a_s_register = 0

    if light:
        a_type = char.l_attack_types
        a_sprites = char.l_attack_sprites
    else:
        a_type = char.h_attack_types
        a_sprites = char.h_attack_sprites

    if not char.is_moving and not char.is_jumping:
        char.is_attacking = True

    if char.attack_verifier == 0:
        char.current_sprite = 0

    for index, attack in enumerate(a_type):
        if attack_k == attack:
            tools.animate_char(char, a_sprites[index])

            a_s_register = a_sprites[index]

    char.attack_verifier += 1

    if char.attack_verifier > len(a_s_register):
        char.attack_verifier = 0
        char.is_attacking = False

        if not is_player:
            return True
    else:
        if not is_player:
            return False


def activate_rules(system, attack_k, obj, player=True):
    """
    > Controla a perda de vida, com base nos multiplicadores de cada ataque, através do sistema FightSystem.

    :param system: O objeto que representa o FightSystem.
    :param attack_k: A variável que guarda o tipo de ataque, do player ou inimigo.
    :param player: True para servir o player, False para o foe (ambos de classe Character).
    :return: Nada.
    """

    if player:
        l_damage = system.foe_atk * 11 // 100
        h_damage = system.foe_atk * 13 // 100

        if obj.is_defending:
            l_damage = system.foe_atk * 11 // 100 - (system.foe_atk * 11 // 100) * 70 // 100
            h_damage = system.foe_atk * 13 // 100 - (system.foe_atk * 11 // 100) * 70 // 100

        if attack_k in system.l_attack_types:
            system.player_hp -= database.get_multipliers(light=True)[system.foe.character][attack_k] + l_damage
            damage_register = database.get_multipliers(light=True)[system.foe.character][attack_k] + l_damage

            if not system.player_hp < 0 and not system.foe_energy >= system.energy_max:
                system.foe_energy += 1

        elif attack_k in system.h_attack_types:
            system.player_hp -= database.get_multipliers(light=False)[system.foe.character][attack_k] + h_damage
            damage_register = database.get_multipliers(light=False)[system.foe.character][attack_k] + h_damage

            if not system.player_hp < 0 and not system.foe_energy >= system.energy_max:
                system.foe_energy += 2

        else:
            system.player_hp -= database.get_ult_multipliers()[system.foe.character]
            damage_register = database.get_ult_multipliers()[system.foe.character]

        if not system.player_hp < 0:
            system.p_life_size -= damage_register * system.p_life_proportion
            system.p_life_bar_outline_rect[0] += damage_register * system.p_life_proportion
        else:
            system.p_life_size = 0
            system.p_life_bar_outline_rect[0] = system.p_life_bar_outline_rect[2] - 2

    else:
        l_damage = system.player_atk * 11 // 100
        h_damage = system.player_atk * 13 // 100

        if obj.is_defending:
            l_damage = system.player_atk * 11 // 100 - (system.player_atk * 11 // 100) * 80 // 100
            h_damage = system.player_atk * 13 // 100 - (system.player_atk * 11 // 100) * 80 // 100

        if attack_k in system.l_attack_types:
            system.foe_hp -= database.get_multipliers(light=True)[system.player.character][attack_k] + l_damage
            damage_register = database.get_multipliers(light=True)[system.player.character][attack_k] + l_damage

            if not system.foe_hp < 0 and not system.player_energy >= system.energy_max:
                system.player_energy += 1

        elif attack_k in system.h_attack_types:
            system.foe_hp -= database.get_multipliers(light=False)[system.player.character][attack_k] + h_damage
            damage_register = database.get_multipliers(light=False)[system.player.character][attack_k] + h_damage

            if not system.foe_hp < 0 and not system.player_energy >= system.energy_max:
                system.player_energy += 2

        else:
            system.foe_hp -= database.get_ult_multipliers()[system.player.character]
            damage_register = database.get_ult_multipliers()[system.player.character]

        if not system.foe_hp < 0:
            system.f_life_size -= damage_register * system.f_life_proportion
        else:
            system.f_life_size = 3
