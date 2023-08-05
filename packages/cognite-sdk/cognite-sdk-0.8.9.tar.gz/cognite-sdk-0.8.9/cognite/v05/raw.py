
'Raw Module\n\nThis module mirrors the Raw API. It allows the user to handle raw data.\n\nhttps://doc.cognitedata.com/0.5/#Cognite-API-Cloud-Raw\n'
import cognite._utils as _utils
import cognite.config as config
from cognite.v05.dto import RawResponse, RawRow

def get_databases(limit=None, cursor=None, api_key=None, project=None):
    'Returns a RawObject containing a list of raw databases.\n\n    Args:\n        limit (int):    A limit on the amount of results to return.\n\n        cursor (str):   A cursor can be provided to navigate through pages of results.\n\n        api_key (str):  Your api-key.\n\n        project (str):  Project name.\n\n    Returns:\n        v05.dto.RawResponse: A data object containing the requested data with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw'.format(project))
    params = {'limit': limit, 'cursor': cursor}
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.get_request(url=url, params=params, headers=headers, cookies=config.get_cookies())
    return RawResponse(res.json())

def create_databases(database_names, api_key=None, project=None):
    'Creates databases in the Raw API and returns the created databases.\n\n    Args:\n        database_names (list):  A list of databases to create.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n    Returns:\n        v05.dto.RawResponse: A data object containing the requested data with several getter methods with different\n        output formats.\n\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/create'.format(project))
    body = {'items': [{'dbName': '{}'.format(database_name)} for database_name in database_names]}
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.post_request(url=url, body=body, headers=headers, cookies=config.get_cookies())
    return RawResponse(res.json())

def delete_databases(database_names, recursive=False, api_key=None, project=None):
    'Deletes databases in the Raw API.\n\n    Args:\n        database_names (list):  A list of databases to delete.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n    Returns:\n        An empty response.\n\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/delete'.format(project))
    body = {'items': [{'dbName': '{}'.format(database_name)} for database_name in database_names]}
    params = {'recursive': recursive}
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.post_request(url=url, body=body, params=params, headers=headers, cookies=config.get_cookies())
    return res.json()

def get_tables(database_name=None, limit=None, cursor=None, api_key=None, project=None):
    'Returns a RawObject containing a list of tables in a raw database.\n\n    Args:\n        database_name (str):   The database name to retrieve tables from.\n\n        limit (int):    A limit on the amount of results to return.\n\n        cursor (str):   A cursor can be provided to navigate through pages of results.\n\n        api_key (str):  Your api-key.\n\n        project (str):  Project name.\n\n    Returns:\n        v05.dto.RawResponse: A data object containing the requested data with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/{}'.format(project, database_name))
    params = dict()
    if (not limit):
        params['limit'] = limit
    if (not cursor):
        params['cursor'] = cursor
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.get_request(url=url, params=params, headers=headers, cookies=config.get_cookies())
    return RawResponse(res.json())

def create_tables(database_name=None, table_names=None, api_key=None, project=None):
    'Creates tables in the given Raw API database.\n\n    Args:\n        database_name (str):    The database to create tables in.\n\n        table_names (list):     The table names to create.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n    Returns:\n        v05.dto.RawResponse: A data object containing the requested data with several getter methods with different\n        output formats.\n\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/{}/create'.format(project, database_name))
    body = {'items': [{'tableName': '{}'.format(table_name)} for table_name in table_names]}
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.post_request(url=url, body=body, headers=headers, cookies=config.get_cookies())
    return RawResponse(res.json())

def delete_tables(database_name=None, table_names=None, api_key=None, project=None):
    'Deletes databases in the Raw API.\n\n    Args:\n        database_name (str):    The database to create tables in.\n\n        table_names (list):     The table names to create.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n    Returns:\n        An empty response.\n\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/{}/delete'.format(project, database_name))
    body = {'items': [{'tableName': '{}'.format(table_name)} for table_name in table_names]}
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.post_request(url=url, body=body, headers=headers, cookies=config.get_cookies())
    return res.json()

def get_rows(database_name=None, table_name=None, limit=None, cursor=None, api_key=None, project=None):
    'Returns a RawObject containing a list of rows.\n\n    Args:\n        database_name (str):    The database name to retrieve rows from.\n\n        table_name (str):       The table name to retrieve rows from.\n\n        limit (int):            A limit on the amount of results to return.\n\n        cursor (str):           A cursor can be provided to navigate through pages of results.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n    Returns:\n        v05.dto.RawResponse: A data object containing the requested data with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/{}/{}'.format(project, database_name, table_name))
    params = dict()
    params['limit'] = limit
    params['cursor'] = cursor
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.get_request(url=url, params=params, headers=headers, cookies=config.get_cookies())
    return RawResponse(res.json())

def create_rows(database_name=None, table_name=None, rows=None, api_key=None, project=None, ensure_parent=False, use_gzip=False):
    "Creates tables in the given Raw API database.\n\n    Args:\n        database_name (str):    The database to create rows in.\n\n        table_name (str):       The table names to create rows in.\n\n        rows (list[v05.dto.RawRow]):            The rows to create.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n        ensure_parent (bool):   Create database/table if it doesn't exist already\n\n        use_gzip (bool):        Compress content using gzip\n\n    Returns:\n        An empty response\n\n    "
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/{}/{}/create'.format(project, database_name, table_name))
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    if ensure_parent:
        params = {'ensureParent': 'true'}
    else:
        params = {}
    ul_row_limit = 1000
    i = 0
    while (i < len(rows)):
        body = {'items': [{'key': '{}'.format(row.key), 'columns': row.columns} for row in rows[i:(i + ul_row_limit)]]}
        res = _utils.post_request(url=url, body=body, headers=headers, params=params, cookies=config.get_cookies(), use_gzip=use_gzip)
        i += ul_row_limit
    return res.json()

def delete_rows(database_name=None, table_name=None, rows=None, api_key=None, project=None):
    'Deletes rows in the Raw API.\n\n    Args:\n        database_name (str):    The database to create tables in.\n\n        table_name (str):      The table name where the rows are at.\n\n        rows (list):            The rows to delete.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n    Returns:\n        An empty response.\n\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/{}/{}/delete'.format(project, database_name, table_name))
    body = {'items': [{'key': '{}'.format(row.key), 'columns': row.columns} for row in rows]}
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.post_request(url=url, body=body, headers=headers, cookies=config.get_cookies())
    return res.json()

def get_row(database_name=None, table_name=None, row_key=None, api_key=None, project=None):
    'Returns a RawObject containing a list of rows.\n\n    Args:\n        database_name (str):    The database name to retrieve rows from.\n\n        table_name (str):       The table name to retrieve rows from.\n\n        row_key (str):          The key of the row to fetch.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n    Returns:\n        v05.dto.RawResponse: A data object containing the requested data with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(api_key, project)
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/raw/{}/{}/{}'.format(project, database_name, table_name, row_key))
    params = dict()
    headers = {'api-key': api_key, 'content-type': '*/*', 'accept': 'application/json'}
    res = _utils.get_request(url=url, params=params, headers=headers, cookies=config.get_cookies())
    return RawResponse(res.json())
