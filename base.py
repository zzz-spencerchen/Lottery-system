

'''
    import user,json
    import gift.json
'''

from common.utils import check_file, timestamp_to_string
from common.error import UserExistsError, RuleError, LevelError, NegativeNumberError
from common.consts import RULES, FIRSTLEVEL, SECONDLEVEL

import os
import time
import json
import multiprocessing

class Base():
    def __init__(self, user_json, gift_json):
        self.user_json = user_json
        self.gift_json = gift_json

        self.__check_user_json()    # check file is legal, type, exist
        self.__check_gift_json()    # check file is legal, type, exist
        self.__init_gifts()   # set gift.json format
        manager = multiprocessing.Manager()
        self.__lock = manager.Lock()


    def __check_user_json(self):
        check_file(self.user_json)


    def __check_gift_json(self):
        check_file(self.gift_json)


    def __read_users(self, time_to_str=False):
        with open(self.user_json, 'r') as f:
            data = json.loads(f.read())  # data is a dictionary

        if time_to_str == True:
            for username,v in data.items():
                v['create_time'] = timestamp_to_string(v['create_time'])
                v['update_time'] = timestamp_to_string(v['update_time'])
                data[username] = v
        return data


    def __write_user(self, **user):
        if 'username' not in user:
            raise ValueError('missing username')
        if 'rule' not in user:
            raise ValueError('missing role')

        # user['active'] = False
        user['create_time'] = time.time()
        user['update_time'] = time.time()  # update is same as create when it create
        user['gifts'] = []


        users = self.__read_users()  # users = {username: {username, active....}}
        if user['username'] in users:  # check username already exist
            raise UserExistsError('username {} is existed'.format(user['username']))

        users.update(
            {user['username']: user}  # update the dict
        )

        self.__save(users, self.user_json)


    def __change_rule(self, username, rule):
        users = self.__read_users()
        user = users.get(username)   # user = value = {username, active, rule...}
        if not user:
            raise ValueError('this username is not exist')

        if rule not in RULES:
            raise RuleError('this is not a valid rule')

        user['rule'] = rule
        user['update_time'] = time.time()
        users[username] = user   # renew value

        self.__save(users, self.user_json)
        return True


    def __change_active(self, username):
        users = self.__read_users()
        user = users.get(username)   # user = value = {username, active, rule...}
        if not user:
            raise ValueError('this username is not exist')

        user['active'] = not user['active']
        user['update_time'] = time.time()

        users[username] = user

        self.__save(users, self.user_json)
        return True


    def __delete_user(self, username):
        users = self.__read_users()
        user = users.get(username)  # user = value = {username, active, rule...}
        if not user:
            raise ValueError('this username is not exist')

        after_delete = users.pop(username)

        self.__save(users, self.user_json)

        return after_delete


    def __read_gifts(self):
        with open(self.gift_json, 'r') as f:
            data = json.loads(f.read())
        return data


    def __init_gifts(self):   # set up gift format
        data = {
            'level1': {
                'level1': {},
                'level2': {},
                'level3': {}
            },
            'level2': {
                'level1': {},
                'level2': {},
                'level3': {}
            },
            'level3': {
                'level1': {},
                'level2': {},
                'level3': {}
            },
            'level4': {
                'level1': {},
                'level2': {},
                'level3': {}
            }
        }

        gifts = self.__read_gifts()  # gifts is a dict
        if len(gifts) != 0:
            return

        self.__save(data, self.gift_json)


    def __check_and_getgift(self, first_level, second_level, gift_name):
        if first_level not in FIRSTLEVEL:
            raise LevelError('first level is not valid')

        if second_level not in SECONDLEVEL:
            raise LevelError('second level is not valid')

        gifts = self.__read_gifts()

        level_one = gifts[first_level]
        level_two = level_one[second_level]

        if gift_name not in level_two:
            return False

        return {'level_one': level_one, 'level_two': level_two, 'gifts': gifts}


    def __write_gift(self, first_level, second_level, gift_name, gift_count):
        if first_level not in FIRSTLEVEL:
            raise LevelError('first level is not valid')

        if second_level not in SECONDLEVEL:
            raise LevelError('second level is not valid')

        gifts = self.__read_gifts()

        current_gift_pool = gifts[first_level]
        current_gift_second_pool = current_gift_pool[second_level]

        if not isinstance(gift_count, int):
            raise TypeError('count need to be int')

        if gift_count <=0:
            gift_count = 1

        if gift_name in current_gift_second_pool:
            current_gift_second_pool[gift_name]['count'] = current_gift_second_pool[gift_name]['count'] + gift_count
        else:
            current_gift_second_pool[gift_name] = {
                'name': gift_name,
                'count': gift_count
            }

        gifts[first_level][second_level] = current_gift_second_pool

        self.__save(gifts, self.gift_json)


    def __gift_update(self, first_level, second_level, gift_name, gift_count=1, is_admin=False):
        data = self.__check_and_getgift(first_level, second_level, gift_name)

        if data == False:
            return data

        current_gift_pool = data.get('level_one')
        current_second_gift_pool = data.get('level_two')
        gifts = data.get('gifts')

        if not isinstance(gift_count, int):
            raise TypeError('count need to be int')

        current_gift = current_second_gift_pool[gift_name]

        if is_admin == True:
            if gift_count <= 0:
                raise ValueError('gift count should larger then 0')
            current_gift['count'] = gift_count
        else:
            if current_gift['count'] - gift_count < 0:
                raise NegativeNumberError('gift count should lower current gift number')
            current_gift['count'] = current_gift['count'] - gift_count

        current_second_gift_pool[gift_name] = current_gift
        current_gift_pool[second_level] = current_second_gift_pool
        gifts[first_level] = current_gift_pool

        self.__save(gifts, self.gift_json)

    def __gift_delete(self, first_level, second_level, gift_name):
        data = self.__check_and_getgift(first_level, second_level, gift_name)

        if data == False:
            return data

        current_gift_pool = data.get('level_one')
        current_second_gift_pool = data.get('level_two')
        gifts = data.get('gifts')

        delete_data = current_second_gift_pool.pop(gift_name)
        current_gift_pool[second_level] = current_second_gift_pool
        gifts[first_level] = current_gift_pool

        self.__save(gifts, self.gift_json)
        return delete_data


    def __save(self, data, path):
        try:
            self.__lock.acquire()
            json_data = json.dumps(data)
            with open(path, 'w') as f:
                f.write(json_data)
        finally:
            self.__lock.release()






if __name__ == '__main__':
    gift_path = os.path.join(os.getcwd(), 'storage', 'gift.json')
    user_path = os.path.join(os.getcwd(), 'storage', 'user.json')
    # print(gift_path)
    # print(user_path)
    base = Base(user_json=user_path, gift_json=gift_path)

    # base.write_user(username='die', rule='admin')  # test write in json

    # result = base.delete_user(username='die')   # test change rule/active/delete function
    # print(result)

    # result = base.read_gifts()
    # print(result)
    # base.gift_update(first_level='level1', second_level='level2', gift_name='Iphone12', gift_count=5)