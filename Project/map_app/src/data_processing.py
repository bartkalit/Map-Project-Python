import pandas as pd
import numpy as np
import os
import timeit

from .users_controller.user_list import UserList
from .traveltime_controller import TravelTime

from math import radians, sin, cos, sqrt, atan2
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import BallTree
from scipy.spatial import distance_matrix
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from queue import PriorityQueue
import networkx as nx
import heapq


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

    def get_user_locations(self, user_id : int, num_of_records : int):
        user_locations = self.data.loc[self.data.user_id == user_id].head(num_of_records)
        return user_locations

    def get_last_visited_location(self, user_id : int):
        user_locations = self.data.loc[self.data.user_id == user_id]
        last_time_update = user_locations["checkin_time"].min()
        last_location_index = user_locations.loc[
            user_locations["checkin_time"] == last_time_update
            ].index
        return self.data.iloc[last_location_index]

    def get_first_visited_location(self, user_id : int):
        user_locations = self.data.loc[self.data.user_id == user_id]
        last_time_update = user_locations["checkin_time"].max()
        last_location_index = user_locations.loc[
            user_locations["checkin_time"] == last_time_update
            ].index
        return self.data.iloc[last_location_index]

    def get_unvisited_locations(self, user_id : int):
        user_loc = self.data.loc[self.data["user_id"] == user_id]
        user_loc_id = user_loc['location_id'].values

        other_loc = self.data.loc[self.data["user_id"] != user_id]
        univisted = other_loc[~(other_loc['location_id'].isin(user_loc_id))]
        return univisted

    def get_unvisited_2hop_locations(self, user_id : int):
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
    def haversine_formula(start_lat : float, start_lng : float, dest_lat : float, dest_lng : float):
        start_lat = start_lat.iloc[0]
        start_lng = start_lng.iloc[0]

        start_lat, start_lng, dest_lat, dest_lng = map(radians, [start_lat, start_lng, dest_lat, dest_lng])
        earth_r = 6371
        dlat = dest_lat - start_lat
        dlng = dest_lng - start_lng

        a = sin(dlat / 2) ** 2 + cos(start_lat) * cos(dest_lat) * sin(dlng) ** 2
        distance = 2 * earth_r * atan2(sqrt(a), sqrt(1 - a))

        return distance

    def add_distance(self, start_location : pd.DataFrame, locations : pd.DataFrame):
        new_locations = locations.copy()
        new_locations['dist'] = new_locations.apply(lambda row: self.haversine_formula(
            start_lat=start_location['lat'],
            start_lng=start_location['lng'],
            dest_lat=row['lat'],
            dest_lng=row['lng']
        ), axis=1)
        return new_locations

    def add_travel_time(self, start_location : pd.DataFrame, locations : pd.DataFrame, transport : str):
        new_locations = locations.copy()
        locations_time_travel = self.traveltime.get_locations_time_travel(
            start_location,
            locations,
            transport)
        new_locations["duration"] = None
        for location in locations_time_travel:
            travel_time = location["properties"]["travel_time"]
            new_locations.at[int(location["id"]), "duration"] = travel_time
        return new_locations

    def find_k_closest_locations_balltree(self, k : int, start_loc : pd.DataFrame, dest_loc : pd.DataFrame, transport : str):
        dest = dest_loc[['lat', 'lng']].values
        start = start_loc[['lat', 'lng']].values
        tree = BallTree(dest, leaf_size=30)
        n_neighbors = k * 4 if k * 4 < len(dest) else len(dest)
        nearest = tree.query(start, k=n_neighbors, return_distance=False)
        closest = dest_loc.iloc[nearest[0].tolist()]
        closest = self.add_travel_time(start_loc, closest, transport)
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

        data = self.find_k_closest_locations_balltree(k, last_loc, dist_loc, "walking+ferry")
        return data

    def get_k_closest_2hop_locations(self, user_id:int, k:int=10):
        last_loc = self.get_last_visited_location(user_id)
        dist_loc = self.get_unvisited_2hop_locations(user_id)
        dist_loc = dist_loc.drop_duplicates(subset=['location_id'])
        
        if dist_loc.empty:
            return dist_loc

        if len(dist_loc) < k:
            k = len(dist_loc)
        
        data = self.find_k_closest_locations_balltree(k, last_loc, dist_loc, "walking+ferry")
        return data

    def get_k_point_shortest_route(self, user_id : int , start : (float, float), end : (float, float), max_nodes=10):
        data = self.get_unvisited_locations(user_id)
        # Prepare start location
        start_loc = self.get_first_visited_location(user_id).copy()
        start_loc['lat'], start_loc['lng'] = start
        start_loc['location_id'] = -1
        # Prepare end location
        end_loc = start_loc.copy()
        end_loc['lat'], end_loc['lng'] = end
        end_loc['location_id'] = -2

        # Find time to get straight from start ot end location
        base_time = self.add_travel_time(start_loc, end_loc, "driving+ferry").iloc[0]['duration']
        base_time = base_time + 200

        # Prepare dataframe for all gathered locations
        checked_locations = pd.concat([start_loc, end_loc], axis=0)
        
        # Prepare dictionary for finding shortest time from start location to given point
        # it stores tuples in format (parent_location_id, time_from_parent_location)
        dist_val = {}
        dist_val[start_loc.iloc[0]['location_id']] = (None, 0)
        dist_val[end_loc.iloc[0]['location_id']] = (start_loc.iloc[0]['location_id'], base_time)

        # Add start and end point to the priority queue
        next_locations = PriorityQueue()
        next_locations.put((0, start_loc.iloc[0]['location_id']))
        next_locations.put((base_time, end_loc.iloc[0]['location_id']))

        counter = 0
        last_loc = start_loc
        visited_loc = []
        # Basic route have start and end location
        longest_route = 2

        while not next_locations.empty():
            if longest_route == max_nodes:
                break

            if counter >= 10:
                break

            route_time, loc_id = next_locations.get()
            last_loc = checked_locations[checked_locations['location_id'] == loc_id]
            if loc_id == end_loc.iloc[0]['location_id']:
                break
            visited_loc.append(loc_id)
            # Get nearest locations without last_loc that is added in front
            dest_loc = self.find_k_closest_locations_balltree(1000, last_loc, data, "driving+ferry").iloc[1:]
            dest_loc.drop_duplicates(subset=['location_id'], keep='first', inplace=True)
            
            end_time_loc = self.add_travel_time(end_loc, dest_loc, "driving+ferry")
            
            checked_locations = pd.concat([checked_locations, dest_loc], axis=0)
            checked_locations.drop_duplicates(subset=['location_id'], keep='first', inplace=True)
            
            for i in range(len(dest_loc)):
                current_loc = dest_loc.iloc[[i]]
                current_id = current_loc.iloc[0]['location_id']

                if current_id not in visited_loc:
                    time_to_end = end_time_loc.iloc[[i]].iloc[0]['duration']
                    if time_to_end != None:
                        current_time = current_loc.iloc[0]['duration']
                        if current_time != None:
                            current_id = current_id
                            prev_time, route_len = self.get_time(dist_val, loc_id)
                            if route_len > longest_route:
                                longest_route = route_len
                            total_time = prev_time + current_time + time_to_end - ((current_time / 5) * (1 - (0.1 * route_len))) - (route_len * 20)
                            if total_time < base_time:
                                if current_id in dist_val:
                                    _, shortest_time = dist_val[current_id]
                                    if shortest_time > current_time:
                                        dist_val[current_id] = (last_loc.iloc[0]['location_id'], current_time)
                                else:
                                    dist_val[current_id] = (last_loc.iloc[0]['location_id'], current_time)
                                next_locations.put((total_time, current_id))
                                _, time = dist_val[end_loc.iloc[0]['location_id']]
                                if total_time < time:
                                    dist_val[end_loc.iloc[0]['location_id']] = (current_id, total_time)
            counter += 1

        result = pd.DataFrame()
        loc_id = end_loc.iloc[0]['location_id']
        while loc_id != None:
            parent_id, time = dist_val[loc_id]

            prev_loc = checked_locations[checked_locations['location_id'] == loc_id].copy()
            prev_time, _ = self.get_time(dist_val, loc_id)
            prev_loc['duration'] = prev_time
            result = pd.concat([prev_loc, result])

            loc_id = parent_id

        return result

    @staticmethod
    def get_time(durations, location_id : int):
        total_time = 0
        length = 0
        prev_loc = location_id
        while prev_loc != None:
            parent_loc, time = durations[prev_loc]
            total_time += time
            prev_loc = parent_loc
            length += 1
        return (total_time, length)
