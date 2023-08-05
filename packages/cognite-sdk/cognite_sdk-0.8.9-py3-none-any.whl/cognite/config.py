
'Project Configuration Module.\n\nThis module allows you to set an api-key and a project for your python project.\n'
from cognite._constants import BASE_URL, RETRY_LIMIT
_CONFIG_API_KEY = ''
_CONFIG_PROJECT = ''
_CONFIG_COOKIES = {}
_CONFIG_BASE_URL = None
_CONFIG_RETRIES = None

def configure_session(api_key='', project='', cookies=None):
    'Sets session variables.\n\n    Args:\n        api_key (str):  Api-key for current project.\n\n        cookies (dict): Cookies to pass with requests.\n\n        project (str):  Project name for current project.\n    '
    global _CONFIG_API_KEY, _CONFIG_COOKIES, _CONFIG_PROJECT
    _CONFIG_API_KEY = api_key
    _CONFIG_PROJECT = project
    _CONFIG_COOKIES = ({} if (cookies is None) else cookies)

def get_config_variables(api_key, project):
    'Returns current project config variables unless other is specified.\n\n    Args:\n        api_key (str):  Other specified api-key.\n\n        project (str):  Other specified project name.\n\n    Returns:\n        tuple: api-key and project name belonging to current project unless other is specified.\n    '
    if (api_key is None):
        api_key = _CONFIG_API_KEY
    if (project is None):
        project = _CONFIG_PROJECT
    return (api_key, project)

def get_cookies():
    'Returns cookies set for the current session.\n\n    Returns:\n        dict: Cookies for current session.\n    '
    return _CONFIG_COOKIES

def set_base_url(url=None):
    'Sets the base url for requests made from the SDK.\n\n    Args:\n        url (str):  URL to set. Set this to None to use default url.\n    '
    global _CONFIG_BASE_URL
    _CONFIG_BASE_URL = url

def get_base_url(api_version=None):
    'Returns the current base url for requests made from the SDK.\n    Args:\n        api_version (float): Version of API to use for base_url\n    Returns:\n        str: current base url.\n    '
    if (not api_version):
        api_version = '<version>'
    return ((_CONFIG_BASE_URL or BASE_URL) + str(api_version))

def set_number_of_retries(retries=None):
    'Sets the number of retries attempted for requests made from the SDK.\n\n    Args:\n        retries (int):  Number of retries to attempt. Set this to None to use default num of retries.\n    '
    global _CONFIG_RETRIES
    _CONFIG_RETRIES = retries

def get_number_of_retries():
    'Returns the current number of retries attempted for requests made from the SDK.\n\n    Returns:\n        int: current number of retries attempted for requests.\n    '
    return (RETRY_LIMIT if (_CONFIG_RETRIES is None) else _CONFIG_RETRIES)
