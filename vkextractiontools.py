# Скрипт позволяет извлекать некоторые данные из профилей Вконтакте в обход их настроек приватности.

import os
import argparse
import vk_api

from vkextractor import VKExtractor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', '-l',
                        help='Логин учётной записи VK, из под которой будут производиться запросы к API VK')
    parser.add_argument('--password', '-p',
                        help='Пароль учётной записи VK, из под которой будут производиться запросы к API VK')
    parser.add_argument('--id', '-i', help='ID пользователя, чьи параметры будут извлекаться')
    parser.add_argument('--day', '-d', action='store_true', help='Извлечь день рождения пользователя')
    parser.add_argument('--month', '-m', action='store_true', help='Извлечь месяц рождения пользователя')
    parser.add_argument('--year', '-y', action='store_true', help='Извлечь год рождения пользователя')
    parser.add_argument('--min-year', type=int, default=1980,
                        help='С какого года начинать перебор. Минимальный год, принимаемый API VK - 1900.'
                             'Значение по умолчанию - 1980')
    parser.add_argument('--max-year', type=int, default=2002,
                        help='Каким годом заканчивать перебор. Значение по умолчанию - 2002')
    parser.add_argument('--status', '-s', action='store_true', help='Извлечь семейное положение пользователя')
    parser.add_argument('--religion', '-r', action='store_true', help='Извлечь мировоззрение пользователя')
    parser.add_argument('--reg-date', action='store_true', help='Извлечь мировоззрение пользователя')

    try:
        args = parser.parse_args()

        if args.min_year < 1900:
            raise Exception('Аргумент опции --min-year должен быть >= 1900')

        if args.min_year > args.max_year:
            raise Exception('Аргумент опции --min-year должен быть <=  аргумента опции --max-year')

        if args.login is None:
            args.login = input('Введите логин учетной записи Вконтакте, '
                               'из под которой будут осуществляться запросы к API VK: ')

        if args.login is not None and args.password is None:
            args.password = input('Введите пароль от учетной записи Вконтакте с логином ' + args.login + ": ")

        if args.id is None:
            args.id = input('Введите ID пользователя, чьи данные будут извлекаться,'
                            'например, durov, либо id228322187: ')

        extractor = VKExtractor(args.login, args.password)

        profile_id, profile_first_name, profile_nickname, profile_second_name =\
            extractor.get_values_for_display_name(args.id)
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
            print('Год рождения: ' + str(extractor.extract_year(profile_id, args.min_year, args.max_year,
                                                                display_name)))
        if args.status:
            print('Семейное положение: ' + str(extractor.extract_status(profile_id, display_name)))
        if args.religion:
            print('Мировоззрение: ' + str(extractor.extract_religion(profile_id, display_name)))
        if args.reg_date:
            date = VKExtractor.get_profile_registration_day(
                extractor.get_profile_id_by_screen_name(args.id))
            print('Дата создания аккаунта: ' + date[2] + '.' + date[1] + '.' + date[0])

    except vk_api.exceptions.BadPassword:
        print('Введены невалидные учетные данные, повторите попытку')
        raise SystemExit

    except vk_api.exceptions.ApiError as error:
        if error.code == 113:
            print('Указан ID несуществующего профиля, повторите попытку')
        raise SystemExit

    except Exception as error:
        print(error)
        raise SystemExit

    finally:
        if os.path.isfile("./vk_config.v2.json"):
            os.remove('./vk_config.v2.json')


if __name__ == "__main__":
    main()
