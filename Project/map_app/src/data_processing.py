import pandas as pd
import numpy as np
import os
import timeit

from .users_controller.user_list import UserList
from .traveltime_controller import TravelTime

from math import radians, sin, cos, sqrt, atan2
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import BallTree


class MapData:
    def __init__(self):
        file_path = os.path.join(os.path.dirname(__file__), "data/Checkins_data.txt")
        columns = ["user_id", "checkin_time", "lat", "lng", "location_id"]
        self.data = pd.read_csv(file_path, sep="\t", header=None, names=columns)
        self.data["checkin_time"] = pd.to_datetime(self.data["checkin_time"])
        self.traveltime = TravelTime()
        self.user_list = UserList()

    def get_data(self):
        return self.data

    def get_user_locations(self, user_id, num_of_records):
        user_locations = self.data.loc[self.data.user_id == user_id].head(num_of_records)
        return user_locations

    def get_last_visited_location(self, user_id):
        user_locations = self.data.loc[self.data.user_id == user_id]
        last_time_update = user_locations["checkin_time"].min()
        last_location_index = user_locations.loc[
            user_locations["checkin_time"] == last_time_update
            ].index
        return self.data.iloc[last_location_index]

    def get_second_last_visited_location(self, user_id):
        user_locations = self.data.loc[self.data.user_id == user_id]
        last_time_update = user_locations["checkin_time"].nsmallest(2).iloc[-1]
        last_location_index = user_locations.loc[
            user_locations["checkin_time"] == last_time_update
            ].index
        return self.data.iloc[last_location_index]

    def get_unvisited_locations(self, user_id):
        user_loc = self.data.loc[self.data["user_id"] == user_id]
        user_loc_id = user_loc['location_id'].values

        other_loc = self.data.loc[self.data["user_id"] != user_id]
        univisted = other_loc[~(other_loc['location_id'].isin(user_loc_id))]
        return univisted

    def get_unvisited_2hop_locations(self, user_id):
        user_loc = self.data.loc[self.data["user_id"] == user_id]
        user_loc_id = user_loc['location_id'].values
        hop_friends_ids = self.user_list.get_2_hop_friends_ids(user_id)
        
        if len(hop_friends_ids) == 0:
            return pd.DataFrame(columns=user_loc.columns)

        other_loc = self.data.loc[self.data["user_id"] != user_id]
        hop_loc = other_loc[np.isin(other_loc['user_id'], hop_friends_ids)]
        univisted = hop_loc[~(hop_loc['location_id'].isin(user_loc_id))]
        return univisted

    @staticmethod
    def haversine_formula(start_lat, start_lng, dest_lat, dest_lng):
        start_lat = start_lat.iloc[0]
        start_lng = start_lng.iloc[0]

        start_lat, start_lng, dest_lat, dest_lng = map(radians, [start_lat, start_lng, dest_lat, dest_lng])
        earth_r = 6371
        dlat = dest_lat - start_lat
        dlng = dest_lng - start_lng

        a = sin(dlat / 2) ** 2 + cos(start_lat) * cos(dest_lat) * sin(dlng) ** 2
        distance = 2 * earth_r * atan2(sqrt(a), sqrt(1 - a))

        return distance

    @staticmethod
    def phitagoras_formula(start_lat, start_lng, dest_lat, dest_lng):
        start_lat = start_lat.iloc[0]
        start_lng = start_lng.iloc[0]

        distance = sqrt(pow(start_lat + dest_lat,2) + pow(start_lng + dest_lng, 2))

        return distance

    def add_distance(self, start_location, locations):
        new_locations = locations.copy()
        new_locations['dist'] = new_locations.apply(lambda row: self.haversine_formula(
            start_lat=start_location['lat'],
            start_lng=start_location['lng'],
            dest_lat=row['lat'],
            dest_lng=row['lng']
        ), axis=1)
        return new_locations

    def add_travel_time(self, start_location, locations):
        new_locations = locations.copy()
        locations_time_travel = self.traveltime.get_locations_time_travel(
            start_location,
            locations,
            "walking+ferry")
        new_locations["duration"] = None
        for location in locations_time_travel:
            travel_time = location["properties"]["travel_time"]
            new_locations.at[int(location["id"]), "duration"] = travel_time
        return new_locations

    def find_k_closest_locations_harvestine(self, k : int, start_loc : pd.DataFrame, dest_loc : pd.DataFrame):
        new_loc = self.add_distance(start_loc, dest_loc)
        return new_loc
    
    def find_k_closest_locations_by_lat_lng(self, k : int, start_loc : pd.DataFrame, dest_loc : pd.DataFrame):
        dest = dest_loc[['lat', 'lng']]
        start = start_loc[['lat', 'lng']]
        nn = NearestNeighbors(metric="haversine", algorithm='ball_tree')
        nn.fit(dest)
        n_neighbors = k * 5 if k * 5 < len(dest) else len(dest)
        nearest = nn.kneighbors(start, n_neighbors=n_neighbors, return_distance=False)
        closest = dest_loc.iloc[nearest[0].tolist()]
        closest = self.add_travel_time(start_loc, closest)
        closest = closest.sort_values(by=['duration'], ascending=True)
        closest = closest.head(k)
        closest = pd.concat([start_loc, closest.loc[:]]).reset_index(drop=True)
        return closest

    def find_k_closest_locations_balltree(self, k : int, start_loc : pd.DataFrame, dest_loc : pd.DataFrame):
        dest = dest_loc[['lat', 'lng']].values
        start = start_loc[['lat', 'lng']].values
        tree = BallTree(dest, leaf_size=30)
        n_neighbors = k * 5 if k * 5 < len(dest) else len(dest)
        nearest = tree.query(start, k=n_neighbors, return_distance=False)
        closest = dest_loc.iloc[nearest[0].tolist()]
        closest = self.add_travel_time(start_loc, closest)
        closest = closest.sort_values(by=['duration'], ascending=True)
        closest = closest.head(k)
        closest = pd.concat([start_loc, closest.loc[:]]).reset_index(drop=True)
        return closest

    def get_k_closest_locations(self, user_id:int, k:int=10):
        last_loc = self.get_last_visited_location(user_id)
        dist_loc = self.get_unvisited_locations(user_id)
        dist_loc = dist_loc.drop_duplicates(subset=['location_id'])

        if dist_loc.empty:
            return dist_loc

        if len(dist_loc) < k:
            k = len(dist_loc)

        data = self.find_k_closest_locations_balltree(k, last_loc, dist_loc)
        return data

    def get_k_closest_2hop_locations(self, user_id:int, k:int=10):
        last_loc = self.get_last_visited_location(user_id)
        dist_loc = self.get_unvisited_2hop_locations(user_id)
        dist_loc = dist_loc.drop_duplicates(subset=['location_id'])
        
        if dist_loc.empty:
            return dist_loc

        if len(dist_loc) < k:
            k = len(dist_loc)
        
        data = self.find_k_closest_locations_balltree(k, last_loc, dist_loc)
        return data
