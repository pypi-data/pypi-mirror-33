import sys

if sys.version_info[0] < 3:
    from authentication import login_required
    from errors import Error
    from network import NetworkManager
    from utils import green
else:
    from structure.authentication import login_required
    from structure.errors import Error
    from structure.network import NetworkManager
    from structure.utils import green

class Lifecycle(object):

    @staticmethod
    @login_required
    def set_status(app, status):
        data = {
            'application_name': app,
            'status': status,
        }

        try:
            endpoint = '/cli/{}/status'.format(app)
            response = NetworkManager.POST_JSON(
                endpoint=endpoint,
                json_data=data,
            )

            success = response['success']
            if success:
                return None
            else:
                if 'message' in response:
                    return Error.warn(response['message'])

            return Error.warn("Request failed.")
        except Exception as e:
            return Error.warn("Request failed.")
