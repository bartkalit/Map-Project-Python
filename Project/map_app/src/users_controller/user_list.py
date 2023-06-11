import pandas as pd
import os
import timeit

from .user import User
from typing import Type


class UserList:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        parent_dri = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dri, "data/Social_Network.txt")
        columns = ["user_id", "friend_id"]
        self.data = pd.read_csv(file_path, sep="\t", header=None, names=columns)
        self.__users = []
        self.__duplicates = True
        self.data = self.remove_duplicates()
        self.create_social_network()

    def add_user(self, user_id : int):
        new_user = User(user_id)
        self.__users.append(new_user)
        return new_user

    def find_user_by_id(self, user_id : int):
        for user in self.__users:
            if user.get_id() == user_id:
                return user
        return None

    def get_user_by_id(self, user_id : int):
        user = self.find_user_by_id(user_id)
        if user is None:
            user = self.add_user(user_id)
        return user     

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
        curr_user = None
        curr_user_id = None
        for _, row in self.data.head(10).iterrows():
            if curr_user_id != row['user_id']:
                curr_user_id = row['user_id']
                curr_user = self.get_user_by_id(curr_user_id)
            
            friend = self.get_user_by_id(row['friend_id'])

            curr_user.add_friend(friend, self.__duplicates)
            friend.add_friend(curr_user, self.__duplicates)
    
    def print_social_network(self):
        print("Users:")
        users = self.get_users()
        users_ids = [u.get_id() for u in users]
        print(users_ids)
        print("Tree:")
        for user in users:
            print(f"User {user.get_id()}:")
            friends_ids = [f.get_id() for f in user.get_friends()]
            print(friends_ids)

    def get_2_hop_friends(self, user_id : int):
        user = self.find_user_by_id(user_id)
        if user is None:
            return []
        
        user_friends = user.get_friends()
        hop_friends = user_friends.copy()
        for friend in user_friends:
            friend_friends = friend.get_friends()
            for hop_friend in friend_friends:
                if hop_friend is not user and hop_friend not in user_friends:
                    hop_friends.append(hop_friend)
        return hop_friends
        
    def get_2_hop_friends_ids(self, user_id : int):
        hop_friends = self.get_2_hop_friends(user_id)
        return [f.get_id() for f in hop_friends]


# users = UserList()
# print(users.data)
# start_time = timeit.default_timer()
# data = users.remove_duplicates()
# users.create_social_network()
# friends = users.get_2_hop_friends(2)
# friends = users.get_2_hop_friends(22)
# print(data.shape)
# print(f"Creating social network took {timeit.default_timer() - start_time} s")

# # users.print_social_network()

# start_time = timeit.default_timer()
# users.data = users.remove_duplicates()
# users.create_social_network()
# friends = users.get_2_hop_friends(2)
# friends = users.get_2_hop_friends(22)
# print(data.shape)
# print(f"Creating social network + removing duplicates took {timeit.default_timer() - start_time} s")

# start_time = timeit.default_timer()
# friends = users.get_2_hop_friends(2)
# print(data.shape)
# print(f"Finding 2 hop friends took {timeit.default_timer() - start_time} s")
# print([friend.get_id() for friend in friends])
