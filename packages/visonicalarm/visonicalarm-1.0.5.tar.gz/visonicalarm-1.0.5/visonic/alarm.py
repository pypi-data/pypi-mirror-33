import json
import requests

from time import sleep
from datetime import datetime


class API(object):
    """ Class used for communication with the Visonic API """

    # Client configuration
    __app_type = 'com.visonic.PowerMaxApp'
    __user_agent = 'Visonic%20GO/2.8.62.91 CFNetwork/901.1 Darwin/17.6.0'
    __rest_version = '4.0'
    __hostname = 'visonic.tycomonitor.com'
    __user_code = '1234'
    __user_id = '00000000-0000-0000-0000-000000000000'
    __panel_id = '123456'
    __partition = 'ALL'

    # The Visonic API URLs used
    __url_base = None
    __url_version = None
    __url_is_panel_exists = None
    __url_login = None
    __url_status = None
    __url_alarms = None
    __url_alerts = None
    __url_troubles = None
    __url_is_master_user = None
    __url_general_panel_info = None
    __url_events = None
    __url_wakeup_sms = None
    __url_all_devices = None
    __url_arm_home = None
    __url_arm_home_instant = None
    __url_arm_away = None
    __url_arm_away_instant = None
    __url_disarm = None
    __url_locations = None
    __url_active_users_info = None
    __url_set_date_time = None
    __url_allow_switch_to_programming_mode = None

    # API session token
    __session_token = None

    def __init__(self, hostname, user_code, user_id, panel_id, partition):
        """ Class constructor initializes all URL variables. """

        # Set connection specific details
        self.__hostname = hostname
        self.__user_code = user_code
        self.__user_id = user_id
        self.__panel_id = panel_id
        self.__partition = partition

        # Visonic API URLs that should be used
        self.__url_base = 'https://' + self.__hostname + '/rest_api/' + self.__rest_version

        self.__url_version = 'https://' + self.__hostname + '/rest_api/version'
        self.__url_is_panel_exists = self.__url_base + '/is_panel_exists?panel_web_name=' + self.__panel_id
        self.__url_login = self.__url_base + '/login'
        self.__url_status = self.__url_base + '/status'
        self.__url_alarms = self.__url_base + '/alarms'
        self.__url_alerts = self.__url_base + '/alerts'
        self.__url_troubles = self.__url_base + '/troubles'
        self.__url_is_master_user = self.__url_base + '/is_master_user'
        self.__url_general_panel_info = self.__url_base + '/general_panel_info'
        self.__url_events = self.__url_base + '/events'
        self.__url_wakeup_sms = self.__url_base + '/wakeup_sms'
        self.__url_all_devices = self.__url_base + '/all_devices'
        self.__url_arm_home = self.__url_base + '/arm_home'
        self.__url_arm_home_instant = self.__url_base + '/arm_home_instant'
        self.__url_arm_away = self.__url_base + '/arm_away'
        self.__url_arm_away_instant = self.__url_base + '/arm_away_instant'
        self.__url_disarm = self.__url_base + '/disarm'
        self.__url_locations = self.__url_base + '/locations'
        self.__url_active_users_info = self.__url_base + '/active_users_info'
        self.__url_set_date_time = self.__url_base + '/set_date_time'
        self.__url_allow_switch_to_programming_mode = self.__url_base + '/allow_switch_to_programming_mode'

    def __send_get_request(self, url, with_session_token):
        """ Send a GET request to the server. Includes the Session-Token only if with_session_token is True. """

        # Prepare the headers to be sent
        headers = {
            'Host': self.__hostname,
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.__user_agent,
            'Accept-Language': 'en-us',
            'Accept-Encoding': 'br, gzip, deflate'
        }

        # Include the session token in the header
        if with_session_token:
            headers['Session-Token'] = self.__session_token

        # Perform the request and raise an exception if the response is not OK (HTML 200)
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.status_code == requests.codes.ok:
            value = json.loads(response.content.decode('utf-8'))
            return value

    def __send_post_request(self, url, data_json, with_session_token):
        """ Send a POST request to the server. Includes the Session-Token only if with_session_token is True. """

        # Prepare the headers to be sent
        headers = {
            'Host': self.__hostname,
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': self.__user_agent,
            'Content-Length': str(len(data_json)),
            'Accept-Language': 'en-us',
            'Accept-Encoding': 'br, gzip, deflate'
        }

        # Include the session token in the header
        if with_session_token:
            headers['Session-Token'] = self.__session_token

        # Perform the request and raise an exception if the response is not OK (HTML 200)
        response = requests.post(url, headers=headers, data=data_json)
        response.raise_for_status()

        # Check HTTP response code
        if response.status_code == requests.codes.ok:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    ######################
    # Public API methods #
    ######################

    @property
    def session_token(self):
        """ Property to keep track of the session token """
        return self.__session_token

    def get_version_info(self):
        """ Find out which REST API versions are supported """
        return self.__send_get_request(self.__url_version, with_session_token=False)

    def get_panel_exists(self):
        """ Check if our panel exists on the server """
        return self.__send_get_request(self.__url_is_panel_exists, with_session_token=False)

    def login(self):
        """ Try to login and get a session token """
        # Setup authentication information
        login_info = {
            'user_code': self.__user_code,
            'app_type': self.__app_type,
            'user_id': self.__user_id,
            'panel_web_name': self.__panel_id
        }

        login_json = json.dumps(login_info, separators=(',', ':'))
        res = self.__send_post_request(self.__url_login, login_json, with_session_token=False)
        self.__session_token = res['session_token']

    def is_logged_in(self):
        """ Check if the session token is still valid """
        try:
            self.get_status()
            return True
        except requests.HTTPError:
            return False

    def get_status(self):
        """ Get the current status of the alarm system """
        return self.__send_get_request(self.__url_status, with_session_token=True)

    def get_alarms(self):
        """ Get the current alarms """
        return self.__send_get_request(self.__url_alarms, with_session_token=True)

    def get_alerts(self):
        """ Get the current alerts """
        return self.__send_get_request(self.__url_alerts, with_session_token=True)

    def get_troubles(self):
        """ Get the current troubles """
        return self.__send_get_request(self.__url_troubles, with_session_token=True)

    def is_master_user(self):
        """ Check if the current user is a master user """
        ret = self.__send_get_request(self.__url_is_master_user, with_session_token=True)
        return ret['is_master_user']

    def get_general_panel_info(self):
        """ Get the general panel information """
        return self.__send_get_request(self.__url_general_panel_info, with_session_token=True)

    def get_events(self):
        """ Get the alarm panel events """
        return self.__send_get_request(self.__url_events, with_session_token=True)

    def get_wakeup_sms(self):
        """ Get the information needed to send a wakeup SMS to the alarm system """
        return self.__send_get_request(self.__url_wakeup_sms, with_session_token=True)

    def get_all_devices(self):
        """ Get the device specific information """
        return self.__send_get_request(self.__url_all_devices, with_session_token=True)

    def get_locations(self):
        """ Get all locations in the alarm system """
        return self.__send_get_request(self.__url_locations, with_session_token=True)

    def get_active_user_info(self):
        """ Get information about the active users. Note: Only master users can see the active_user_ids! """
        return self.__send_get_request(self.__url_active_users_info, with_session_token=True)

    def set_date_time(self):
        """ Set the time on the alarm panel. Note: Only master users can set the time! """

        # Make sure the time has the correct format: 20180704T185700
        current_time = datetime.now().isoformat().replace(':', '').replace('.', '').replace('-', '')[:15]

        time_info = {'time': current_time}
        time_json = json.dumps(time_info, separators=(',', ':'))
        return self.__send_post_request(self.__url_set_date_time, time_json, with_session_token=True)

    def arm_home(self, partition):
        """ Arm in Home mode and with Exit Delay """
        arm_info = {'partition': partition}
        arm_json = json.dumps(arm_info, separators=(',', ':'))
        return self.__send_post_request(self.__url_arm_home, arm_json, with_session_token=True)

    def arm_home_instant(self, partition):
        """ Arm in Home mode instantly (without Exit Delay) """
        arm_info = {'partition': partition}
        arm_json = json.dumps(arm_info, separators=(',', ':'))
        return self.__send_post_request(self.__url_arm_home_instant, arm_json, with_session_token=True)

    def arm_away(self, partition):
        """ Arm in Away mode and with Exit Delay """
        arm_info = {'partition': partition}
        arm_json = json.dumps(arm_info, separators=(',', ':'))
        return self.__send_post_request(self.__url_arm_away, arm_json, with_session_token=True)

    def arm_away_instant(self, partition):
        """ Arm in Away mode instantly (without Exit Delay) """
        arm_info = {'partition': partition}
        arm_json = json.dumps(arm_info, separators=(',', ':'))
        return self.__send_post_request(self.__url_arm_away_instant, arm_json, with_session_token=True)

    def disarm(self, partition):
        """ Disarm the alarm system """
        disarm_info = {'partition': partition}
        disarm_json = json.dumps(disarm_info, separators=(',', ':'))
        return self.__send_post_request(self.__url_disarm, disarm_json, with_session_token=True)
