from options import SETTINGS_PATHS
import os


def get_settings(settings_type):
    """
    :param settings_type: either 'sql' or 'import'
    :return:
    """
    if os.path.isdir(SETTINGS_PATHS['docker'][settings_type]):
        return SETTINGS_PATHS['docker'][settings_type]
    else:
        script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir, SETTINGS_PATHS['default'][settings_type])
