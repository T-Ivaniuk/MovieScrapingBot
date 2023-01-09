import random
import time
import json
import datetime
import os
import asyncio
import aiohttp
import pandas as pd
import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "x_developer": "ENOVAX", "content-type": "application/json; charset=UTF-8",
    "sec-ch-ua-platform": "Windows", "origin": "https://www.gv.com.sg",
    "accept": "application/json, text/plain, */*",
    "authority": "www.gv.com.sg"}

cinema_data = []
cinema_column_names = ["Cinema", "Movie", "Day", "Time", "Number of seats",
                       "Sold", "Available", "WB_available", "Sold %"]


def random_n():
    return random.randint(1, 999)


def timestamp_now():
    return int(time.time() * 1000)


def save_sheet(dataframe, sheet_name, filename):
    if os.path.isfile(filename):
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            time.sleep(0.1)
    else:
        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)


def validate_sheet_name(string: str) -> str:
    """sheet name validation for excel file with filter match and symbol length"""
    available = " 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    name = "".join(filter(lambda x: x in available, string))[:30]
    if len(name) > 0:
        return name
    else:
        return f"sheet {random_n()}"


async def get_showtime_data(cinemaid, filmcode, showdate, showtime, hallnumber, session):
    """get data of sold and available seats for specific movie session"""
    payload = {"cinemaId": cinemaid, "filmCode": filmcode, "showDate": showdate,
               "showTime": showtime, "hallNumber": hallnumber}
    response = await session.post(url=f"https://www.gv.com.sg/.gv-api/seatplan?t={random_n()}_{timestamp_now()}",
                                  headers=headers, data=json.dumps(payload))
    response_json = await response.json()
    return response_json


async def get_count_of_seats(response):
    """data manipulation for count of available and sold seats"""
    data = {"Sold": 0, "%": 0, "Available": 0, "WB_available": 0}
    for row in response["data"]:
        for column in row:
            if column["status"] == "B":
                data["Sold"] += 1
            if column["status"] == "L":
                data["Available"] += 1
            if column["status"] == "W":
                data["Available"] += 1
                data["WB_available"] += 1
    seats_count = data['Sold'] + data['Available']
    pers_v = round(data['Sold'] / seats_count, 5) * 100
    data['Sold %'] = " " + "{:.1f}".format(pers_v)
    data["Number of seats"] = seats_count
    return data


async def parse_movie(cinema_name, cinema_code, movie, session):
    """parse specific movie in each cinema"""
    try:
        movies_data = []
        film_title = movie["filmTitle"]
        film_code = movie["filmCd"]
        for showtime in movie["times"]:
            hall = showtime["hall"]
            human_time = showtime["time24"]
            showdate = showtime['showDate']
            response = await get_showtime_data(cinemaid=cinema_code, filmcode=film_code, showdate=showdate,
                                               showtime=human_time, hallnumber=hall, session=session)
            seats_dict = await get_count_of_seats(response)
            seats_dict["Movie"] = film_title
            seats_dict["Day"] = showdate
            seats_dict["Time"] = human_time
            seats_dict["Cinema"] = cinema_name
            movies_data.append(seats_dict)

        return movies_data
    except Exception as E:
        print(E)
    finally:
        return []


class GoldenVillage:

    def __init__(self, day):

        self.day = day
        self.preparired_cinema_list = None
        self.cinema_list = None
        self.movies_list = None
        self.all_cinemas_list = None
        self.day_in_timestamp = None
        self.fully_fixed_cinema_data = None

    def get_specific_timestamp(self):
        """function to convert specific day in timestamp format"""
        datetime_now = datetime.datetime.now(datetime.timezone.utc)
        self.day_in_timestamp = int((datetime.datetime(datetime_now.year, datetime_now.month, datetime_now.day, 00, 00)
                                     + datetime.timedelta(days=self.day)).timestamp()) * 1000

    def get_cinema_list(self):
        response = requests.post(url=f"https://www.gv.com.sg/.gv-api/cinemas?t={random_n()}_{timestamp_now()}",
                                 headers=headers).json()
        self.cinema_list = response["data"]

    def get_movies_list(self):
        self.get_specific_timestamp()
        payload = {"cinemaId": "", "filmCode": "", "date": self.day_in_timestamp, "advanceSales": False}
        response = requests.post(url=f"https://www.gv.com.sg/.gv-api/v2buytickets?t={random_n()}_{timestamp_now()}",
                                 headers=headers, data=json.dumps(payload)).json()
        self.movies_list = response["data"]["cinemas"]

    def prepare_cinema_list(self):
        """function of adding films for each of the cinemas"""
        self.get_movies_list()
        self.get_cinema_list()
        result_d = {}
        for cinema in self.cinema_list:
            for movie in self.movies_list:
                if cinema["id"] == movie["id"]:
                    cinema["movies"] = movie["movies"]
                    result_d[len(result_d)] = cinema
        self.preparired_cinema_list = result_d

    def delete_cinema_without_movies(self):
        keys_to_del = []
        for cinema in self.preparired_cinema_list:
            if len(self.preparired_cinema_list[cinema]["movies"]) == 0:
                keys_to_del.append(cinema)
        for key in keys_to_del:
            del self.preparired_cinema_list[key]

    def fix_midnight_datetime(self):
        """function which allows to fix midnight session datetime issue"""
        for cinema in self.preparired_cinema_list:
            for movie in self.preparired_cinema_list[cinema]["movies"]:
                for time_data in movie["times"]:
                    if (len(time_data['time24']) == 3 and int(time_data['time24'][0]) < 7) or len(str(
                            time_data['time24'])) <= 2:
                        showdate = datetime.datetime.strptime(time_data['showDate'], '%d-%m-%Y')
                        time_data['showDate'] = (showdate + datetime.timedelta(days=1)).strftime('%d-%m-%Y')
        self.fully_fixed_cinema_data = self.preparired_cinema_list


async def get_cinema(cinema, session):
    cinema_d = []
    cinema_name = cinema['name']
    cinema_code = cinema['id']
    for movie in cinema['movies']:
        movie_data = await parse_movie(cinema_name=cinema_name, cinema_code=cinema_code, movie=movie,
                                       session=session)
        for movie_d in movie_data:
            cinema_d.append(movie_d)

    cinema_data.append((cinema_name, cinema_d))


async def get_movie_session_data(day):
    gv_cinema = GoldenVillage(day=day)
    gv_cinema.prepare_cinema_list()
    gv_cinema.delete_cinema_without_movies()
    gv_cinema.fix_midnight_datetime()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for cinema in gv_cinema.preparired_cinema_list.values():
            task = asyncio.create_task(get_cinema(cinema, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


def gv_parser(day, filename):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.new_event_loop().run_until_complete(get_movie_session_data(day))
    for each_cinema in cinema_data:
        each_cinema_name = each_cinema[0]
        each_cinema_data = each_cinema[1]
        each_cinema_dataframe = pd.DataFrame(data=each_cinema_data, columns=cinema_column_names)
        save_sheet(dataframe=each_cinema_dataframe, sheet_name=validate_sheet_name(each_cinema_name), filename=filename)
    return filename
