from .user import User
from typing import Type

class UserList:
    def __init__(self):
        self.__users = []

    def add_user(self, user : Type['User']):
        self.users.append(user)

    def get_user_by_id(self, user_id : int):
        for user in self.__users:
            if user.get_id() == user_id:
                return user
        return None

    def remove_user(self, user : Type['User'] = None, user_id : int = None):
        if user:
            self.__users.remove(user)
        elif user_id:
            self.__users.remove(self.get_user_by_id(user_id))
    
    def get_users(self):
        return self.__users