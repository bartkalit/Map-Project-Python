import pandas as pd

class MapData:
    def __init__(self):
        # self.data = pd.read_csv('map_app/static/map_app/Checkins_data.txt', sep="\t", header=None)
        self.data = pd.read_csv('static/map_app/Checkins_data.txt', sep="\t", header=None)
        self.data.columns = ["UserID", "Checkin_time", "lat", "lng", "LocationID"]

    def get_lat_long(self, num_of_records=20):
        return self.data[["lat", "lng"]].head(num_of_records).to_json(orient="records")

    def get_user_locations(self, user_id, num_of_records):
        user_locations = self.data.loc[self.data.UserID == user_id].head(num_of_records)
        return user_locations

    def get_data(self):
        return self.data

    def get_last_visited_location(self, user_id):
        user_locations = self.data.loc[self.data.UserID == user_id]
        user_locations.loc[:, ("Checkin_time")] = pd.to_datetime(user_locations["Checkin_time"])
        last_time_update = user_locations["Checkin_time"].min()
        last_location = user_locations.loc[user_locations["Checkin_time"] == last_time_update]
        return last_location

    def get_unvisited_locations(self, user_id):
        unvisited_locations = self.data.loc[self.data["UserID"] != user_id]
        return unvisited_locations

    def add_distance(self, start_location, locations):
        new_locations = locations
        new_locations['dist'] = sqrt(pow(new_locations['lot'] + start_location['lot'], 2) + pow(new_locations['lng'] + start_location['lng'], 2))
        print(new_locations['dist'].head(20))


map = MapData()
data = map.add_distance(map.get_last_visited_location(2), map.get_unvisited_locations(2))
print(data)
        