import pandas as pd
import os
import timeit

from user import User
from typing import Type


class UserList:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        parent_dri = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dri, "data/Social_Network.txt")
        columns = ["user_id", "friend_id"]
        self.data = pd.read_csv(file_path, sep="\t", header=None, names=columns)
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

    def print_data(self, k):
        print(self.data.head(k))

    def remove_duplicates(self):
        slim_data = self.data


        slim_data['check_string'] = slim_data.apply(lambda row: ''.join(sorted([str(row['user_id']), str(row['friend_id'])])), axis=1)
        slim_data = slim_data.drop_duplicates(subset=["check_string"], keep="first")
        return slim_data

    def create_social_network(self):
        for _, row in self.data.head(10).iterrows():
            print(row)

users = UserList()
start_time = timeit.default_timer()
data = users.remove_duplicates()
print(data.shape)
# print(''.join(sorted([str(1), str(2)])))
print(f"BallTree method took {timeit.default_timer() - start_time} s")