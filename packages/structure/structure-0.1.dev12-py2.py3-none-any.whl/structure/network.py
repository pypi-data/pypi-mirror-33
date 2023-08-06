import json
import sys
import requests

if sys.version_info[0] < 3:
    from config import ConfigManager
    from errors import Error
else:
    from structure.config import ConfigManager
    from structure.errors import Error

STRUCTURE_URL = 'https://structure.sh'
X_STRUCTURE_TOKEN = 'X-Structure-Token'

REQUEST_FAILED = 'Request failed. Please contact us if this error persists.'

class NetworkManager(object):

    @staticmethod
    def POST_JSON(endpoint, json_data={}, files=None):
        request = requests.post(
            url=STRUCTURE_URL + endpoint,
            headers={
                X_STRUCTURE_TOKEN: ConfigManager.get_api_token(),
            },
            json=json_data,
            files=files,
            timeout=20,
        )

        try:
            return json.loads(request.text)
        except Exception as e:
            return REQUEST_FAILED

    @staticmethod
    def POST_form(endpoint, form_data):
        request = requests.post(
            url=STRUCTURE_URL + endpoint,
            data=form_data,
            timeout=20,
        )

        try:
            return json.loads(request.text)
        except Exception as e:
            return REQUEST_FAILED
