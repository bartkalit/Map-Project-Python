import requests
import json

from decouple import config


class TravelTime:
    def __init__(self):
        self.traveltime_api_url = "https://api.traveltimeapp.com/v4/time-filter/fast"

    def traveltime_time_filter(self, request_data):
        try:
            headers = {
                "X-Application-Id": config("TRAVELTIME_API_ID"),
                "X-Api-Key": config("TRAVELTIME_API_KEY"),
                "Content-Type": "application/json"
            }
            response = requests.post(self.traveltime_api_url, headers=headers, data=request_data)
            return response.text
        except Exception as e:
            print("Distance API failed")
            print(e)

    @staticmethod
    def get_time_filter_data(start_location, locations, transportation):
        points = [{
            "id": "start_point",
            "coords": {
                "lat": start_location["lat"].values[0],
                "lng": start_location["lng"].values[0]
            }
        }]
        for idx in locations.index:
            points.append({
                "id": str(idx),
                "coords": {
                    "lat": locations.at[idx, "lat"],
                    "lng": locations.at[idx, "lng"]
                }
            })

        arrival_searches = {
            "one_to_many": [
                {
                    "id": "arrive-at one-to-many search",
                    "arrival_location_ids": [str(i) for i in locations.index],
                    "departure_location_id": "start_point",
                    "properties": ["travel_time"],
                    "arrival_time_period": "weekday_morning",
                    "transportation": {
                        "type": transportation
                    },
                    "travel_time": 1800
                }
            ],
            "many_to_one": []
        }

        request_data = {
            "locations" : points,
            "arrival_searches": arrival_searches
        }

        return json.dumps(request_data)

    def get_locations_time_travel(self, start_location, locations, transportation):
        request_data = self.get_time_filter_data(start_location, locations, transportation)
        result = self.traveltime_time_filter(request_data)
        result = json.loads(result)["results"][0]
        return result["locations"]