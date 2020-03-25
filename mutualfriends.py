# Стандартными средствами ВК через веб интерфейс можно узнать только общих друзей у себя и еще одного профиля.
# Данный скрипт позволяет узнать общих друзей 2 и более профилей ВК.
# При этом не обязательно наличие своего профиля в аргументах опции --ids

import os
import argparse
import vk_api

from vkextractor import VKExtractor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', '-l',
                        help='Логин учётной записи, из под которой будут производиться запросы к API')
    parser.add_argument('--password', '-p',
                        help='Пароль учётной записи, из под которой будут производиться запросы к API')
    parser.add_argument('--ids', '-i', nargs='+', help='ID пользователей, общих друзей которых нужно найти')

    try:
        args = parser.parse_args()

        if args.login is None:
            args.login = input('Введите логин учетной записи Вконтакте, '
                               'из под которой будут осуществляться запросы к API VK: ')

        if args.login is not None and args.password is None:
            args.password = input('Введите пароль от учетной записи Вконтакте с логином ' + args.login + ": ")

        if args.ids is None:
            args.ids = input('Введите ID пользователей, общих друзей которых необходимо найти')

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

    except vk_api.exceptions.BadPassword:
        print('Введены невалидные учетные данные, повторите попытку')
        raise SystemExit

    except vk_api.exceptions.ApiError as error:
        if error.code == 30:
            print("Один из профилей является закрытым по отношению к профилю, из под которого осуществляются запросы. "
                  "Измените профиль в --login, либо закрытый профиль в --ids.")
        if error.code == 113:
            print('Один из введенных ID не является валидным аккаунтом, повторите попытку')
        raise SystemExit

    except Exception as error:
        print(error)
        raise SystemExit

    finally:
        if os.path.isfile("./vk_config.v2.json"):
            os.remove('./vk_config.v2.json')


if __name__ == "__main__":
    main()
