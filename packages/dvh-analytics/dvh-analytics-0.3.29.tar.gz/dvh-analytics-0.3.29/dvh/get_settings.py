from __future__ import print_function
from options import SETTINGS_PATHS
import os


def get_settings(settings_type):
    """
    :param settings_type: either 'sql' or 'import'
    :return:
    """
    print("running get_settings")
    print(SETTINGS_PATHS)
    if os.path.isdir(SETTINGS_PATHS['docker'][settings_type]):
        print("docker detected")
        return SETTINGS_PATHS['docker'][settings_type]
    else:
        script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir, SETTINGS_PATHS['default'][settings_type])
