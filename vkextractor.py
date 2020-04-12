import re
import requests

import vk_api


class VKExtractor:

    def __init__(self, login, password):
        self.__vk_session = vk_api.VkApi(login=login, password=password)
        self.__vk_session.auth()
        self.__vk = self.__vk_session.get_api()

    def is_profile_id_valid(self, profile_id):
        return self.__vk.users.get(user_ids=profile_id)[0]

    def get_values_for_display_name(self, profile_id):
        user_info = self.__vk.users.get(user_ids=profile_id, fields='nickname')[0]
        return user_info['id'], user_info['first_name'], user_info['nickname'], user_info['last_name']

    def get_profile_id_by_screen_name(self, screen_name):
        return self.__vk.utils.resolveScreenName(screen_name=screen_name)['object_id']

    def extract_value(self, profile_id, display_name, values, extract_type):
        for value in values:
            users = self.__vk.execute(code='''
                var container = [];
                var offset = 0;
                var probe = API.users.search({{q:"{0}", {1}:"{2}", count:1000, offset:offset}});
                container.push(probe);
                offset = offset + 1000;
                var iter = (probe.count / 1000) - 1;
                while (iter > 0)
                {{
                    container.push(API.users.search({{q:"{0}", {1}:"{2}", count:1000, offset:offset}}));
                    offset = offset + 1000;
                    iter = iter - 1;
                }};
                return container;
            '''.format(display_name, extract_type, value))
            for user in users[0]['items']:
                if user['id'] == profile_id:
                    return value

    # Данный метод не подходит под паттерн extract_value ввиду особенностей извлечения семейного положения
    def extract_status(self, profile_id, display_name):
        status_description = [
            'не женат(не замужем)',
            'встречается',
            'помолвлен(-а)',
            'женат(замужем)',
            'всё сложно',
            'в активном поиске',
            'влюблен(-а)',
            'в гражданском браке'
        ]
        for status in range(1, 9):
            users = self.__vk.execute(code='''
                var container = [];
                var offset = 0;
                var probe = API.users.search({{q:"{0}", status:{1}, count:1000, offset:offset}});
                container.push(probe);
                offset = offset + 1000;
                var iter = (probe.count / 1000) - 1;
                while (iter > 0)
                {{
                    container.push(API.users.search({{q:"{0}", status:{1}, count:1000, offset:offset}}));
                    offset = offset + 1000;
                    iter = iter - 1;
                }};
                return container;
            '''.format(display_name, status))
            for user in users[0]['items']:
                if user['id'] == profile_id:
                    return status_description[status - 1]

    def get_mutual_friends_list(self, profiles):
        target_uids = ','.join([str(self.get_profile_id_by_screen_name(screen_name)) for screen_name in profiles[1:]])
        response = self.__vk.friends.getMutual(source_uid=self.get_profile_id_by_screen_name(profiles[0]),
                                               target_uids=target_uids)
        mutual_friends = [set(i['common_friends']) for i in response]
        for i in mutual_friends[1:]:
            mutual_friends[0].intersection_update(i)
        return mutual_friends[0]

    @staticmethod
    def get_profile_registration_day(profile_id):
        response = requests.get('https://vk.com/foaf.php?id=' + str(profile_id)).text
        date = re.search('created dc:date="\d{4}-\d{2}-\d{2}', response).group(0)
        return date.split('"')[1].split('-')
