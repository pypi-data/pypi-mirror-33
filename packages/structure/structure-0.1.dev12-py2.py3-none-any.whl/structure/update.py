import yaml
import time
import pipdate
import os
import sys
import pkg_resources

if sys.version_info[0] < 3:
    from errors import Error
    from utils import *
else:
    from structure.errors import Error
    from structure.utils import *

CONFIG_PATH = os.path.expanduser('~/.structure-config.yaml')
LAST_CHECK_KEY = 'last_checked'

# 12 hours
SECONDS_BETWEEN_CHECKS = (60 * 60 * 12)

def check_for_updates_if_needed():
    try:
        if should_check_for_updates():
            current_version = pkg_resources.require("structure")[0].version
            message = pipdate.check('structure', current_version)

            if message:
                print(message)
                print(Error.note('Use {} to upgrade Structure globally.'.format(green('`sudo`'))))

            update_last_check_time()
    except Exception as e:
        return

def should_check_for_updates():
    config_create_if_needed()
    config = get_config()

    if not config:
        return False

    if not LAST_CHECK_KEY in config:
        return False
    
    last_check_time = config[LAST_CHECK_KEY]
    current_time = time.time()

    time_since_last_check = (current_time - last_check_time)

    return (time_since_last_check > SECONDS_BETWEEN_CHECKS)


def update_last_check_time(last_updated=None):
    if not last_updated:
        last_updated = time.time()

    data = {
        LAST_CHECK_KEY: int(last_updated)
    }

    with open(CONFIG_PATH, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

def config_create_if_needed():
    if not os.path.exists(CONFIG_PATH):
        f = open(CONFIG_PATH, 'w')
        f.close()
        update_last_check_time(last_updated=0)

def get_config():
    try:
        with open(CONFIG_PATH, 'r+') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return None
