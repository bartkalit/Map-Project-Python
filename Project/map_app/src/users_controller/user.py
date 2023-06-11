import pandas as pd

from typing import Type

class User:
    def __init__(self, id=-1):
        self.__id = id
        self.__last_location = pd.DataFrame
        self.__friends = []
        self.__unvisited_locations_dist = pd.DataFrame

    def set_id(self, id : int):
        self.__id = id

    def get_id(self):
        return self.__id

    def set_last_loc(self, last_loc : pd.DataFrame):
        self.__last_location = last_loc

    def get_last_loc(self):
        return self.__last_location

    def add_friend(self, user : Type['User'], duplicates : bool=True):
        if duplicates:
            if self.check_if_friend(user):
                return None
        self.__friends.append(user)

    def check_if_friend(self, user : Type['User']):
        for friend in self.__friends:
            if user == friend:
                return True
        return False

    def remove_friend(self, user : Type['User'] = None, friend_id : int = None):
        if user:
            self.__friends.remove(friend)
        elif friend_id:
            for friend in self.__friends:
                if friend.get_id() == friend_id:
                    self.__friends.remove(friend)

    def get_friends(self):
        return self.__friends

    def set_unvisited_locations(self, locations : pd.DataFrame):
        self.__unvisited_locations_dist = locations

    def set_unvisited_locations(self):
        return self.__unvisited_locations_dist
