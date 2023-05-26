import pandas as pd
import numpy as np
import timeit

from math import radians, sin, cos, sqrt, atan2
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import BallTree


class MapData:
    def __init__(self):
        # self.data = pd.read_csv('map_app/static/map_app/Checkins_data.txt', sep="\t", header=None)
        self.data = pd.read_csv('static/map_app/Checkins_data.txt', sep="\t", header=None)
        self.data.columns = ["user_id", "checkin_time", "lat", "lng", "location_id"]
        self.data["checkin_time"] = pd.to_datetime(self.data["checkin_time"])

    def get_lat_long(self, num_of_records=20):
        return self.data[["lat", "lng"]].head(num_of_records).to_json(orient="records")

    def get_user_locations(self, user_id, num_of_records):
        user_locations = self.data.loc[self.data.user_id == user_id].head(num_of_records)
        return user_locations

    def get_data(self):
        return self.data

    def get_last_visited_location(self, user_id):
        user_locations = self.data.loc[self.data.user_id == user_id]
        last_time_update = user_locations["checkin_time"].min()
        last_location_index = user_locations.loc[user_locations["checkin_time"] == last_time_update].index
        return self.data.iloc[last_location_index]

    def get_unvisited_locations(self, user_id):
        user_loc = self.data.loc[self.data["user_id"] == user_id]
        user_loc_id = user_loc['location_id'].values

        other_loc = self.data.loc[self.data["user_id"] != user_id]
        univisted = other_loc[~(other_loc['location_id'].isin(user_loc_id))]
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
        new_locations['dist2'] = new_locations.apply(lambda row: self.phitagoras_formula(
            start_lat=start_location['lat'],
            start_lng=start_location['lng'],
            dest_lat=row['lat'],
            dest_lng=row['lng']
        ), axis=1)
        return new_locations
    
    def find_k_closest_locations_by_lat_lng(self, k : int, start_loc : pd.DataFrame, dest_loc : pd.DataFrame):
        dest = dest_loc[['lat', 'lng']]
        start = start_loc[['lat', 'lng']]
        nn = NearestNeighbors(metric="haversine", algorithm='ball_tree')
        nn.fit(dest)
        nearest = nn.kneighbors(start, n_neighbors=k, return_distance=False)
        closest = dest_loc.iloc[nearest[0].tolist()]
        closest = self.add_distance(start_loc, closest)
        closest = closest.sort_values(by=['dist'], ascending=True)
        closest = pd.concat([start_loc, closest.loc[:]]).reset_index(drop=True)
        return closest

    def find_k_closest_locations_balltree(self, k : int, start_loc : pd.DataFrame, dest_loc : pd.DataFrame):
        dest = dest_loc[['lat', 'lng']].values
        start = start_loc[['lat', 'lng']].values
        tree = BallTree(dest, leaf_size=30)
        nearest = tree.query(start, k=k , return_distance=False)
        closest = dest_loc.iloc[nearest[0].tolist()]
        closest = self.add_distance(start_loc, closest)
        closest = closest.sort_values(by=['dist'], ascending=True)
        closest = pd.concat([start_loc, closest.loc[:]]).reset_index(drop=True)
        return closest

    def get_k_closest_locations_for_user(self, user_id:int, k:int=10, algorithm:str='nn'):
        last_loc = self.get_last_visited_location(user_id)
        dist_loc = self.get_unvisited_locations(user_id)
        dist_loc = dist_loc.drop_duplicates(subset=['location_id'])
        data = pd.DataFrame
        if algorithm == 'nn':
            data = self.find_k_closest_locations_by_lat_lng(k, last_loc, dist_loc)
        else:
            data = self.find_k_closest_locations_balltree(k, last_loc, dist_loc)
        return data


# map_data = MapData()

# start_time = timeit.default_timer()
# data = map_data.get_k_closest_locations_for_user(531, 10, 'nn')
# print(f"Nearest Neighbours method took {timeit.default_timer() - start_time} s")
# print(data)

# start_time = timeit.default_timer()
# data = map_data.get_k_closest_locations_for_user(531, 10, 'bt')
# print(f"BallTree method took {timeit.default_timer() - start_time} s")
# print(data)

# start_time = timeit.default_timer()
# data = map_data.get_k_closest_locations_for_user(22, 10, 'bt')
# print(f"BallTree method took {timeit.default_timer() - start_time} s")
# print(data)