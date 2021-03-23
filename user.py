
from common.error import NotUserError, RuleError, UserActiceError
from common.utils import timestamp_to_string


from base import Base
import os, random, time

class User(Base):
    def __init__(self, username, password, user_json, gift_json):
        self.username = username
        self.password = password
        super().__init__(user_json, gift_json)


        self.get_user()
        self.gift_random = list(range(1,101))


    def get_user(self):
        users = self._Base__read_users()

        if self.username not in users:
            self.__register(self.username, self.password)
            print('please wait for account verification')
            return

        if self.password != users.get(self.username).get('password'):
            raise ValueError('your password {} is not correct'.format(self.password))

        current_user = users.get(self.username)
        if current_user.get('active') == False:
            raise UserActiceError('this user {} can not be used'.format(self.username))

        if current_user.get('rule') != 'normal':
            raise RuleError('you are over the permission')

        self.user = current_user
        self.name = current_user.get('username')
        self.rule = current_user.get('rule')
        self.gifts = current_user.get('gifts')
        self.create_time = timestamp_to_string(current_user.get('create_time'))
        self.update_time = timestamp_to_string(current_user.get('update_time'))
        self.count = current_user.get('count')




    def get_gifts(self):
        gifts = self._Base__read_gifts()
        gift_list = []

        for level_one, level_one_pool in gifts.items():
            # print(level_one_pool)

            for level_two, level_two_pool in level_one_pool.items():
                # print(level_two_pool)

                for gift_name, gift_info in level_two_pool.items():
                    # print(gift_info)
                    gift_list.append(gift_info.get('name'))

        return gift_list


    def user_count(self):
        if self.update_time == timestamp_to_string(time.time()):
            self.count = self.count + 1
        else:
            self.update_time = timestamp_to_string(time.time())
            self.count = 0

        self.__update()


    def choice_gift(self):
        self.get_user()
        self.user_count()

        if self.count > 5:
            raise ValueError('you already tried 5 times today, pls come back tomorrow!!!')

        # level-1 get
        first_level = None
        second_level = None
        level_one_count = random.choice(self.gift_random)

        if 1 <= level_one_count <= 50:
            first_level = 'level1'
        elif 50 < level_one_count <= 80:
            first_level = 'level2'
        elif 80 < level_one_count <= 94:
            first_level = 'level3'
        elif 95 <= level_one_count <= 100:
            first_level = 'level4'
        else:
            raise ValueError('value should between 1-100')

        gifts = self._Base__read_gifts()
        level_one = gifts.get(first_level)
        # print(level_one)

        level_two_count = random.choice(self.gift_random)

        if 1 <= level_two_count <= 80:
            second_level = 'level1'
        elif 80 < level_two_count <= 94:
            second_level = 'level2'
        elif 94 < level_two_count <= 100:
            second_level = 'level3'
        else:
            raise ValueError('value should between 1-100')

        level_two = level_one.get(second_level)
        # print(level_two)

        if len(level_two) == 0:
            print('sorry you are not the lucky one')
            return

        gift_names = []
        for k,v in level_two.items():
            gift_names.append(k)
        gift_name = random.choice(gift_names)
        gift_info = level_two.get(gift_name)
        if gift_info.get('count') <= 0:
            print('sorry you are not the lucky one')
            return

        self._Base__gift_update(first_level=first_level, second_level=second_level,
                                gift_name=gift_name)

        self.user['gifts'].append(gift_name)
        self.__update()
        print('you get the {}'.format(gift_name))



    def __update(self):
        users = self._Base__read_users()
        users[self.username] = self.user
        users[self.username]['count'] = self.count

        self._Base__save(users, self.user_json)



    def __register(self, username, password):
        self._Base__write_user(username=username, password=password, rule='normal', active=False, count=0)






if __name__ == '__main__':

    gift_path = os.path.join(os.getcwd(), 'storage', 'gift.json')
    user_path = os.path.join(os.getcwd(), 'storage', 'user.json')
    user = User(username='BBB', password='123', user_json=user_path, gift_json=gift_path)
    #print(user.get_gifts())
    user.choice_gift()
