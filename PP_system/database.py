from pickle import dump, load
import struct


def get_multipliers(light=True):
    """
    > Pega um dicionário contendo os dicionários dos multiplicadores de golpes básicas para cada personagem.

    :param light: True para o dicionário de Ataques Leves, False para Ataques Pesados.
    :return: Um dos dicionários.
    """

    if light:

        light_attacks = {

            'Caipora': {'Straight Strike': 3,
                        'Rising Strike': 2,
                        'Low Pushed Hit': 4},

            'Boitata': {'Straight Strike': 5,
                        'Rising Strike': 6,
                        'Low Pushed Hit': 4}

        }

        return light_attacks

    else:

        heavy_attacks = {

            'Caipora': {'Quick Assault': 7,
                        'Crescent Assault': 5,
                        'Ground Ring Blow': 6},

            'Boitata': {'Quick Assault': 4,
                        'Crescent Assault': 3,
                        'Ground Ring Blow': 8}
        }

        return heavy_attacks


def get_ult_multipliers():

    ultimates = {'Caipora': 200, 'Boitata': 280}

    return ultimates


def get_ult_commands():

    ult_commands = {'Caipora': 'wsadk', 'Boitata': 'swswdl'}

    return ult_commands


def get_status():
    """
    > Pega um dicionário contendo os dicionários com os STATUS inteiros de cada personagem.

    :return: O dicionário de STATUS.
    """

    char_status = {

        'Caipora':    {'HP': 700, 'ATK': 120, 'DEF': 80,
                       'INT': 70, 'RES': 80},

        'Boitata':    {'HP': 660, 'ATK': 150, 'DEF': 80,
                       'INT': 150, 'RES': 80}

    }

    return char_status
