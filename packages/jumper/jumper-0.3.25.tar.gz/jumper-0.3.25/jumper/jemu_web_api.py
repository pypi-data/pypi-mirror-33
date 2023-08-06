"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function

import os
import sys
from time import sleep
import calendar
import time
import requests
import logging
import Queue
import threading
from __version__ import __version__ as jumper_current_version

API_URL = 'https://vlab.jumper.io/api/v2'
if 'JUMPER_STAGING' in os.environ:
    API_URL = 'https://us-central1-jemu-web-app-staging.cloudfunctions.net/api/v2'
if 'JUMPER_STAGING_INBAR' in os.environ:
    API_URL = 'https://us-central1-jemu-web-app-inbar.cloudfunctions.net/api/v2'


class WebException(Exception):
    pass


class AuthorizationError(WebException):
    def __init__(self, message):
        super(WebException, self).__init__(message)
        self.exit_code = 4
        self.message = message


class UnInitializedError(WebException):
    def __init__(self):
        print("Failed to get user id. Please reach out to support@jumper.io for help")
        super(WebException, self).__init__("Failed to get user id. Please reach out to support@jumper.io for help")
        self.exit_code = 6
        self.message = "Failed to get user id. Please reach out to support@jumper.io for help"


class EmulatorGenerationError(WebException):
    def __init__(self, message):
        super(WebException, self).__init__(message)
        self.exit_code = 5
        self.message = message


class JemuWebApi(object):
    def __init__(self, jumper_token=None, api_url=API_URL, local_jemu=None):
        self._api_url = api_url
        self._token = jumper_token
        self._headers = {'Authorization': 'Bearer ' + self._token}
        self._user_uid = None
        self._local_jemu = local_jemu

        logging.getLogger("requests").setLevel(logging.WARNING)
        res = requests.get(self._api_url + '/hello', headers=self._headers)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == requests.codes['unauthorized'] or res.status_code == requests.codes['forbidden']:
                print("Error: Authorization failed. Check the token in your config.json file")
                raise AuthorizationError("Error: Authorization failed. Check the token in the config.json file.")
            else:
                raise e

        self._user_uid = res.json()['userUid']
        self._threads = []
        self._events_queue = None

        if not self._local_jemu:
            self._events_queue = Queue.Queue()
            self._events_handler_should_run = True
            self._events_handler_thread = threading.Thread(target=self._event_sender)
            self._events_handler_thread.setDaemon(True)
            self._threads.append(self._events_handler_thread)
            self._events_handler_thread.start()

    def upload_file(self, file_path):
        t = threading.Thread(target=self._upload_file, args=[file_path])
        t.start()
        self._threads.append(t)

    def _upload_file(self, filepath):
        filename = os.path.basename(filepath)
        signs = {"$", "#", "[", "]"}
        num_of_signs = filename.count('.') - 1
        filename = filename.replace('.', '_', num_of_signs)
        for i in signs:
            filename = filename.replace(i, '_')

        filename = str(int(calendar.timegm(time.gmtime()))) + '_' + filename
        if self._user_uid is None:
            raise UnInitializedError

        headers = self._headers
        headers['Content-Type'] = 'application/octet-stream'

        success = False
        for try_number in range(3):
            try:
                res = requests.post(
                    '{}/firmwares/upload/{}/{}'.format(self._api_url, self._user_uid, filename),
                    headers=headers
                )
                res.raise_for_status()
                signed_url = res.text
                with open(filepath, 'rb') as data:
                    res = requests.put(signed_url, data=data)
                    res.raise_for_status()
            except requests.HTTPError, requests.ConnectionError:
                sleep(1)
                continue
            success = True
            break

        if not success:
            sys.stderr.write("Error: Could not upload file")

    # def check_status(self, filename):
    #     if self._user_uid is None:
    #         raise UnInitializedError
    #
    #     headers = self._headers
    #     headers['Content-Type'] = 'application/text'
    #     res = requests.get(
    #         '{}/firmwares/{}/{}/status'.format(self._api_url, self._user_uid, filename),
    #         headers=headers
    #     )
    #     return res

    def send_event(self, event_dict):
        if self._user_uid is None:
            raise UnInitializedError
        event_name = event_dict['event']
        event_labels = {}
        if "labels" in event_dict:
            event_labels = event_dict["labels"]
        event_labels['distinct_id'] = self._user_uid
        event_labels['sdk_version'] = jumper_current_version
        event_labels['Operating System'] = sys.platform
        headers = self._headers
        headers['Content-Type'] = 'application/json'
        res = requests.post(
            '{}/analytics/{}/{}'.format(self._api_url, self._user_uid, event_name),
            headers=headers,
            json=event_labels
        )
        return res

    # def check_error(self, filename):
    #     if self._user_uid is None:
    #         raise UnInitializedError
    #
    #     headers = self._headers
    #     headers['Content-Type'] = 'application/text'
    #     res = requests.get(
    #         '{}/firmwares/{}/{}/error'.format(self._api_url, self._user_uid, filename),
    #         headers=headers
    #     )
    #     return res

    def add_event(self, message):
        if self._events_queue:
            self._events_queue.put(message)

    def _event_sender(self):
        while True:
            try:
                cur_event = self._events_queue.get(True, timeout=0.2)
            except Queue.Empty:
                if not self._events_handler_should_run:
                    return
                else:
                    continue
            retries = 3
            while retries > 0:
                try:
                    self.send_event(cur_event)
                except Exception:
                    retries -= 1
                    sleep(1)
                else:
                    break

    def stop(self):
        self._events_handler_should_run = False
        self._stop_threads()

    def _stop_threads(self):
        for t in self._threads:
            if t.is_alive():
                t.join()
