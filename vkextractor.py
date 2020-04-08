import re
import requests

import vk_api


class VKExtractor:

    def __init__(self, login, password):
        self.__vk_session = vk_api.VkApi(login=login, password=password)
        self.__vk_session.auth()
        self.__vk = self.__vk_session.get_api()

    def is_profile_id_valid(self, profile_id):
        return True if self.__vk.users.get(user_ids=profile_id) else False

    def get_values_for_display_name(self, profile_id):
        user_info = self.__vk.users.get(user_ids=profile_id, fields='nickname')[0]
        return user_info['id'], user_info['first_name'], user_info['nickname'], user_info['last_name']

    def get_profile_id_by_screen_name(self, screen_name):
        return self.__vk.utils.resolveScreenName(screen_name=screen_name)['object_id']

    def extract_day(self, profile_id, display_name):
        for birth_day in range(1, 32):
            users = self.__vk.execute(code='''
                var container = [];
                var offset = 0;
                var probe = API.users.search({q:"''' + display_name + '''", birth_day:''' + str(birth_day) + ''',
                                              count:1000, offset:offset});
                container.push(probe);
                offset = offset + 1000;
                var iter = probe.count / 1000;
                while (iter > 0)
                {
                    container.push(API.users.search({q:"''' + display_name + '''", birth_day:''' + str(birth_day) + ''',
                                                     count:1000, offset:offset}));
                    offset = offset + 1000;
                    iter = iter - 1;
                };
                return container;
            ''')
            for user in users[0]['items']:
                if user['id'] == profile_id:
                    return birth_day

    def extract_month(self, profile_id, display_name):
        for birth_month in range(1, 13):
            users = self.__vk.execute(code='''
                var container = [];
                var offset = 0;
                var probe = API.users.search({q:"''' + display_name + '''", birth_month:''' + str(birth_month) + ''',
                                              count:1000, offset:offset});
                container.push(probe);
                offset = offset + 1000;
                var iter = probe.count / 1000;
                while (iter > 0)
                {
                    container.push(API.users.search({q:"''' + display_name + '''", birth_month:''' + str(birth_month) + ''',
                                                     count:1000, offset:offset}));
                    offset = offset + 1000;
                    iter = iter - 1;
                };
                return container;
            ''')
            for user in users[0]['items']:
                if user['id'] == profile_id:
                    return birth_month

    def extract_year(self, profile_id, year_from, year_to, display_name):
        for birth_year in range(year_from, year_to + 1):
            users = self.__vk.execute(code='''
                var container = [];
                var offset = 0;
                var probe = API.users.search({q:"''' + display_name + '''", birth_year:''' + str(birth_year) + ''',
                                              count:1000, offset:offset});
                container.push(probe);
                offset = offset + 1000;
                var iter = probe.count / 1000;
                while (iter > 0)
                {
                    container.push(API.users.search({q:"''' + display_name + '''", birth_year:''' + str(birth_year) + ''',
                                                     count:1000, offset:offset}));
                    offset = offset + 1000;
                    iter = iter - 1;
                };
                return container;
            ''')
            for user in users[0]['items']:
                if user['id'] == profile_id:
                    return birth_year

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
                var probe = API.users.search({q:"''' + display_name + '''", status:''' + str(status) + ''',
                                              count:1000, offset:offset});
                container.push(probe);
                offset = offset + 1000;
                var iter = probe.count / 1000;
                while (iter > 0)
                {
                    container.push(API.users.search({q:"''' + display_name + '''", status:''' + str(status) + ''',
                                                     count:1000, offset:offset}));
                    offset = offset + 1000;
                    iter = iter - 1;
                };
                return container;
            ''')
            for user in users[0]['items']:
                if user['id'] == profile_id:
                    return status_description[status - 1]

    def extract_religion(self, profile_id, display_name):
        religion_description = [
            'Иудаизм',
            'Православие',
            'Католицизм',
            'Протестантизм',
            'Ислам',
            'Буддизм',
            'Конфуцианство',
            'Светский гуманизм',
            'Пастафарианство'
        ]
        for religion in religion_description:
            users = self.__vk.execute(code='''
                var container = [];
                var offset = 0;
                var probe = API.users.search({q:"''' + display_name + '''", religion:"''' + religion + '''",
                                              count:1000, offset:offset});
                container.push(probe);
                offset = offset + 1000;
                var iter = probe.count / 1000;
                while (iter > 0)
                {
                    container.push(API.users.search({q:"''' + display_name + '''", religion:"''' + religion + '''",
                                                     count:1000, offset:offset}));
                    offset = offset + 1000;
                    iter = iter - 1;
                };
                return container;
            ''')
            for user in users[0]['items']:
                if user['id'] == profile_id:
                    return religion

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
