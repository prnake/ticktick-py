from datetime import datetime

import httpx
import os
import pytz

from helpers.time_zone import date_format, convert_local_time_to_utc


def logged_in(func):
    """
    Decorator that will check if the current instance is logged in
    """

    def call(self, *args, **kwargs):
        if not self.access_token:
            raise ValueError('ERROR: Not Logged In')
        return func(self, *args, **kwargs)

    return call


class TickTickClient:
    BASE_URL = 'https://api.ticktick.com/api/v2/'

    def __init__(self, username: str, password: str) -> None:
        """
        Initializes a client session by logging into TickTick
        :param username: TickTick Username
        :param password: TickTick Password
        """
        self.access_token = ''
        self.cookies = {}
        self.login(username, password)

    def login(self, username: str, password: str) -> None:
        """
        Obtains session token
        :param username: TickTick Username
        :param password: TickTick Password
        """
        url = self.BASE_URL + 'user/signon'
        user_info = {
            'username': username,
            'password': password
        }
        parameters = {
            'wc': True,
            'remember': True
        }
        # Make an HTTP POST request
        response = httpx.post(url, json=user_info, params=parameters)

        # Raise error for any status code other than 200 (OK)
        self.check_status_code(response, 'Could Not Log In - Invalid Username or Password')

        response_information = response.json()
        self.access_token = response_information['token']
        self.cookies['t'] = self.access_token

    @staticmethod
    def check_status_code(response, error_message: str) -> None:
        """Makes sure the return on the response was 200"""
        if response.status_code != 200:
            raise ValueError(error_message)

    def create_task(self, task_name: str):
        pass

    def create_tag(self):
        pass

    def create_project(self) -> None:
        pass

    @logged_in
    def delete_list(self, list_id: str) -> None:
        """Deletes the list corresponding to the passed list id number"""
        url = self.BASE_URL + 'batch/project'
        parameters = {
            'delete': [list_id],
        }
        response = httpx.post(url, json=parameters, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Delete List')

    @logged_in
    def get_lists(self) -> dict:
        """Returns a dictionary containing all fields for each list"""
        url = self.BASE_URL + 'projects'
        response = httpx.get(url, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Retrieve Values')

        return response.json()

    @logged_in
    def get_lists_name_and_id(self) -> dict:
        """Returns a dictionary containing -> {project name: id}"""
        request = self.get_lists()
        name_dict = dict()
        for task in request:
            name = task['name']
            task_id = task['id']
            name_dict[name] = task_id

        return name_dict

    @logged_in
    def get_summary(self, time_zone: str, start_date: datetime, end_date: datetime = None, full_day: bool = True) -> list:
        """
        Returns a list containing all the fields for all the completed tasks on the date or range of dates.

        """
        url = self.BASE_URL + 'project/all/completed'

        if time_zone not in pytz.all_timezones_set:
            raise ValueError('Invalid Time Zone')

        if end_date is None:
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = datetime(start_date.year, start_date.month, start_date.day, 23, 59, 59)

        elif full_day is True and end_date is not None:
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

        # Time Range is specific and will stay the same
        start_date = convert_local_time_to_utc(start_date, time_zone)
        end_date = convert_local_time_to_utc(end_date, time_zone)

        parameters = {
            'from': start_date.strftime(date_format),
            'to': end_date.strftime(date_format),
            'limit': 100
        }
        response = httpx.get(url, params=parameters, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Get Values')
        return response.json()

    def start_focus_timer(self):
        """Starts the focus timer"""
        pass

    def start_pomodoro_timer(self):
        pass

    def create_habit(self):
        pass

    def update_habit(self):
        pass

    def create_smart_list(self):
        pass

    def complete_task(self):
        pass

    def get_templates(self):
        # https://api.ticktick.com/api/v2/templates
        pass


if __name__ == '__main__':
    usern = os.getenv('TICKTICK_USER')
    passw = os.getenv('TICKTICK_PASS')
    client = TickTickClient(usern, passw)
    tasks = client.get_summary('US/Pacific', datetime(2020, 12, 10, 8), full_day=False)
    for task in tasks:
        print(task['title'])