
import os


from base import Base
from common.error import NotUserError, UserActiceError, RuleError

class Admin(Base):
    def __init__(self, username, user_json, gift_json):
        self.username = username
        super().__init__(user_json, gift_json)  # admin can have all base __init__ function and value
        self.get_user()


    def get_user(self):
        users = self._Base__read_users()
        current_user = users.get(self.username)

        if current_user == None:
            raise NotUserError('This user is not exist!')

        if current_user.get('active') == False:
            raise UserActiceError('this user {} can not be used'.format(self.username))

        if current_user.get('rule') != 'admin':
            raise RuleError('you have no permission')

        self.user = current_user
        self.rule = current_user.get('rule')
        self.name = current_user.get('username')
        self.active = current_user.get('active')


    def __check(self, message):
        self.get_user()  # every step check this admin user is still admin user
        if self.rule != 'admin':
            raise Exception(message)


    def view_false(self):
        false_list = []
        users = self._Base__read_users()
        for k,v in users.items():
            if v.get('active') == False:
                false_list.append(k)

        print(false_list)


    def add_user(self, username, rule):
        self.__check('you have no permission')

        self._Base__write_user(username=username, rule=rule)


    def update_user_active(self, username):
        self.__check('you have no permission')

        self._Base__change_active(username=username)


    def update_user_rule(self, username, rule):
        self.__check('you have no permission')

        self._Base__change_rule(username=username, rule=rule)


    def add_gift(self, first_level, second_level, gift_name, gift_count):
        self.__check('you have no permission')

        if not isinstance(gift_count, int):
            raise TypeError('count need to be int')

        self._Base__write_gift(first_level=first_level, second_level=second_level,
                               gift_name=gift_name, gift_count=gift_count)


    def delete_gift(self, first_level, second_level, gift_name):
        self.__check('you have no permission')

        self._Base__gift_delete(first_level=first_level, second_level=second_level, gift_name=gift_name)


    def update_gift(self, first_level, second_level, gift_name, gift_count):
        self.__check('you have no permission')

        self._Base__gift_update(first_level=first_level, second_level=second_level,
                                gift_name=gift_name, gift_count=gift_count, is_admin=True)


if __name__ == '__main__':
    gift_path = os.path.join(os.getcwd(), 'storage', 'gift.json')
    user_path = os.path.join(os.getcwd(), 'storage', 'user.json')
    admin = Admin('die', user_path, gift_path)
    # admin.view_false()
    # admin.update_user_rule(username='AAA', rule='admin')
    # admin.update_gift(first_level='level1', second_level='level2', gift_name='Iphone12', gift_count=10)