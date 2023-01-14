import requests
import os
import pandas as pd
import time
import datetime

events_header = \
    {"Accept-Encoding": "gzip, deflate, br",
     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 ",
     "veeziaccesstoken": "sVJR4rtFak-ZQvm87lwoIA2"}

movie_header = \
    {"Accept-Encoding": "gzip, deflate, br",
     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 ",
     "veeziaccesstoken": "8xhbsjcv7n4yw5d9kjrmzk9ecg"}


class TheProjector:

    def __init__(self, filename: str, day: int):

        self.filename = filename
        self.day = day
        self.sheetname = "data"
        self.movies = None
        self.cinema_screen_ids = None
        self.parsed_movie_data = None
        self.parsed_data_frame = None

    def _get_theprojector_cinemas(self):
        response = requests.get(url="https://theprojector.sg/page-data/sq/d/1893686774.json").json()
        cinemas_dict = {}
        for node in response["data"]["allMarkdownRemark"]["edges"]:
            node_list = []
            node_title = node["node"]["frontmatter"]["title"]
            screen_lists = node["node"]["fields"]["venues"]
            for screen_hub in screen_lists:
                screen_list = screen_hub["frontmatter"]["screens"]
                if screen_list is not None:
                    for screen_dict in screen_list:
                        node_list.append(screen_dict["veeziScreenId"])
            cinemas_dict[node_title] = node_list
        self.cinema_screen_ids = cinemas_dict

    def _get_theprojector_movies(self):
        movies = []
        movies.extend(requests.get(url="https://api.us.veezi.com/v1/websession/", headers=headers).json())
        movies.extend(requests.get(url="https://api.us.veezi.com/v1/websession/", headers=headers2).json())
        self.movies = movies

    def _get_cinema_name_by_screen_id(self, screen_id):
        for cinema in self.cinema_screen_ids:
            if screen_id in self.cinema_screen_ids[cinema]:
                return cinema
        return "Cinema not found"

    def _add_cinema_location(self):
        for movie in self.movies:
            movie_screen_id = movie["ScreenId"]
            movie['Cinema'] = self._get_cinema_name_by_screen_id(movie_screen_id)

    def _parse_data(self):
        total_movie_data = []
        for movie in self.movies:
            movie_time = movie["PreShowStartTime"]
            if self._day_filter_hit(movie_time):
                movie_title = movie["Title"]
                cinema_name = movie["Cinema"]
                movie_seats_available = movie["SeatsAvailable"]
                movie_seats_sold = movie["SeatsSold"]
                movie_seats_held = movie["SeatsHeld"]
                movie_seats_house = movie["SeatsHouse"]
                movie_total_seats_count = movie_seats_sold + movie_seats_held + movie_seats_house + movie_seats_available
                pers_v = round(movie_seats_sold / movie_total_seats_count, 5) * 100
                formatted_pers_v = " " + "{:.1f}".format(pers_v)
                total_movie_data.append([cinema_name, movie_title, movie_time, movie_seats_sold,
                                         movie_seats_held, movie_seats_house, movie_seats_available, formatted_pers_v])
        self.parsed_movie_data = total_movie_data

    def _day_filter_hit(self, time_to_check):
        specific_day = (datetime.date.today() + datetime.timedelta(days=self.day)).day
        target_day = datetime.datetime.strptime(time_to_check, '%Y-%m-%dT%H:%M:%S').day
        return target_day == specific_day

    def _create_dataframe(self):
        column_names = ["Cinema name", "Movie name", "Start time", "Sold", "Held", "Seats house", "Available", "Sold %"]
        self.parsed_data_frame = pd.DataFrame(data=self.parsed_movie_data,
                                              columns=column_names).sort_values(by=['Start time'])

    def _save_to_file(self):
        if os.path.isfile(self.filename):
            with pd.ExcelWriter(self.filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.parsed_data_frame.to_excel(writer, sheet_name=self.sheetname, index=False)
                time.sleep(0.1)
        else:
            with pd.ExcelWriter(self.filename, engine='openpyxl', mode='w') as writer:
                self.parsed_data_frame.to_excel(writer, sheet_name=self.sheetname, index=False)

    def parse_to_file(self):
        self._get_theprojector_cinemas()
        self._get_theprojector_movies()
        self._add_cinema_location()
        self._parse_data()
        self._create_dataframe()
        self._save_to_file()
        return self.filename


