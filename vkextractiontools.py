# Скрипт позволяет извлекать некоторые данные из профилей Вконтакте в обход их настроек приватности.

import argparse
from getpass import getpass
import os

import vk_api

from vkextractor import VKExtractor


HELP = '''Usage: vkextractiontools.py [--login LOGIN] [--password PASSWORD] [--id ID] [--day]
                            [--month] [--year] [--year-from YEAR_FROM] [--year-to YEAR_TO]
                            [--status] [--religion] [--reg-date]

Options:
-h, --help          Вывести данную помощь.
-l, --login         Логин учётной записи Вконтакте, из под которой будут производиться запросы к API VK.
-p, --password      Пароль учётной записи Вконтакте, из под которой будут производиться запросы к API VK.
-i, --id            ID пользователя Вконтакте, чьи параметры будут извлекаться.
-d, --day           Извлечь день рождения.
-m, --month         Извлечь месяц рождения.
-y, --year          Извлечь год рождения.
-f, --year-from     С какого года начинать перебор. Минимальный год, принимаемый API VK - 1900.
                    Значение по умолчанию - 1980.
-t, --year-to       Каким годом заканчивать перебор. Значение по умолчанию - 2002.
-s, --status        Извлечь семейное положение.
-r, --religion      Извлечь мировоззрение.
--reg-date          Извлечь дату регистрации.
'''

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h', '--help', action='store_true')
parser.add_argument('-l', '--login')
parser.add_argument('-p', '--password')
parser.add_argument('-i', '--id')
parser.add_argument('-d', '--day', action='store_true')
parser.add_argument('-m', '--month', action='store_true')
parser.add_argument('-y', '--year', action='store_true')
parser.add_argument('-f', '--year-from', type=int, default=1980)
parser.add_argument('-t', '--year-to', type=int, default=2002)
parser.add_argument('-s', '--status', action='store_true')
parser.add_argument('-r', '--religion', action='store_true')
parser.add_argument('--reg-date', action='store_true')

try:
    args = parser.parse_args()

    if args.help:
        print(HELP)
        raise SystemExit

    if args.year_from < 1900:
        raise Exception('Аргумент опции --year-from должен быть >= 1900')

    if args.year_from > args.year_to:
        raise Exception('Аргумент опции --year-from должен быть <=  аргумента опции --year-to')

    if not args.login:
        args.login = input('Введите логин учетной записи Вконтакте, из под которой будут осуществляться запросы к API VK: ')

    if args.login and not args.password:
        args.password = getpass(prompt='Введите пароль от учетной записи Вконтакте с логином ' + args.login + ': ')

    if not args.id:
        args.id = input('Введите ID пользователя, чьи данные будут извлекаться, например, durov, либо id228322187: ')

    extractor = VKExtractor(args.login, args.password)

    profile_id, profile_first_name, profile_nickname, profile_second_name = extractor.get_values_for_display_name(args.id)
    if not profile_nickname:
        display_name = profile_first_name + ' ' + profile_second_name
    else:
        display_name = profile_first_name + ' ' + profile_nickname + ' ' + profile_second_name
    print('Цель:', display_name)

    if args.day:
        print('День рождения: ' + str(extractor.extract_day(profile_id, display_name)))
    if args.month:
        print('Месяц рождения: ' + str(extractor.extract_month(profile_id, display_name)))
    if args.year:
        print('Год рождения: ' + str(extractor.extract_year(profile_id, args.year_from, args.year_to, display_name)))
    if args.status:
        print('Семейное положение: ' + str(extractor.extract_status(profile_id, display_name)))
    if args.religion:
        print('Мировоззрение: ' + str(extractor.extract_religion(profile_id, display_name)))
    if args.reg_date:
        date = VKExtractor.get_profile_registration_day(extractor.get_profile_id_by_screen_name(args.id))
        print('Дата создания аккаунта: ' + date[2] + '.' + date[1] + '.' + date[0])

except KeyboardInterrupt:
    pass

except vk_api.exceptions.BadPassword:
    print('Введены невалидные учетные данные!')

except vk_api.exceptions.ApiError as error:
    if error.code == 113:
        print('Аргументом опции --id является несуществующий профиль Вконтакте!')
    else:
        print('Ошибка ВК с кодом:', error.code)

except Exception as error:
    print(error)

finally:
    if os.path.isfile("./vk_config.v2.json"):
        os.remove('./vk_config.v2.json')
