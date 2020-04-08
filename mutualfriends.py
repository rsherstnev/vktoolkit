# Стандартными средствами ВК через веб интерфейс можно узнать только общих друзей у себя и еще одного профиля.
# Данный скрипт позволяет узнать общих друзей 2 и более профилей ВК.
# При этом не обязательно наличие своего профиля в аргументах опции --ids

import argparse
from getpass import getpass
import os

import vk_api

from vkextractor import VKExtractor


HELP = '''Usage: mutualfriends.py [--login LOGIN] [--password PASSWORD] [--ids ID_1 ID_2...]

Options:
-h, --help          Вывести данную помощь.
-l, --login         Логин учётной записи Вконтакте, из под которой будут производиться запросы к API VK.
-p, --password      Пароль учётной записи Вконтакте, из под которой будут производиться запросы к API VK.
-i, --ids           ID пользователей Вконтакте, общих друзей которых нужно найти.
'''

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h', '--help', action='store_true')
parser.add_argument('-l', '--login')
parser.add_argument('-p', '--password')
parser.add_argument('-i', '--ids', nargs='+')

try:
    args = parser.parse_args()

    if args.help:
        print(HELP)
        raise SystemExit

    if not args.login:
        args.login = input('Введите логин учетной записи Вконтакте, '
                           'из под которой будут осуществляться запросы к API VK: ')

    if args.login and not args.password:
        args.password = getpass(prompt='Введите пароль от учетной записи Вконтакте с логином ' + args.login + ': ')

    if not args.ids:
        args.ids = input('Введите через пробел ID пользователей, общих друзей которых необходимо найти: ').split()

    if len(args.ids) < 2:
        raise Exception("Для нахождения общих друзей необходимо минимум 2 профиля ВК!")

    extractor = VKExtractor(args.login, args.password)

    for profile_id in args.ids:
        extractor.is_profile_id_valid(profile_id)

    mutual_friends = extractor.get_mutual_friends_list(args.ids)

    print('Для следующих профилей: ', sep='\n')
    for profile in args.ids:
        print('https://vk.com/' + str(profile), sep='\n')

    print('Общими друзьями являются:', sep='\n')
    for mutual_friend in mutual_friends:
        print('https://vk.com/id' + str(mutual_friend), sep='\n')

except KeyboardInterrupt:
    pass

except vk_api.exceptions.BadPassword:
    print('Введены невалидные учетные данные, повторите попытку')

except vk_api.exceptions.ApiError as error:
    if error.code == 30:
        print("Один из профилей является закрытым по отношению к профилю, из под которого осуществляются запросы. "
              "Измените профиль в --login, либо закрытый профиль в --ids.")
    elif error.code == 113:
        print('Один из введенных ID не является валидным аккаунтом, повторите попытку')
    else:
        print('Ошибка ВК с кодом:', error.code)

except Exception as error:
    print(error)

finally:
    if os.path.isfile("./vk_config.v2.json"):
        os.remove('./vk_config.v2.json')
