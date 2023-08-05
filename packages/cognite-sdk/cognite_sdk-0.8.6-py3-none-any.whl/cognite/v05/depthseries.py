
'Depthseries Module\n\nThis module mirrors the Timeseries API, but handles pairs of timeseries to emulate depth(or other indexed) data series. It allows you to fetch data from the api and output it in various formats.\n\nhttps://doc.cognitedata.com/0.5/#Cognite-API-Time-series\n'
import re
import sys
import copy
import itertools
from urllib.parse import quote_plus
import cognite._utils as _utils
import cognite.config as config
import cognite.v05.timeseries as ts
from cognite.v05.dto import LatestDatapointResponse, DatapointDepth, TimeSeries, TimeSeriesResponse, Datapoint, TimeseriesWithDatapoints
MS_INCREMENT = 1000

def post_multitag_datapoints(depthseries_with_datapoints, **kwargs):
    'Insert data into multiple depthseries.\n\n        Args:\n            depthseries_with_datapoints (List[v05.dto.DepthseriesWithDatapoints]): The depthseries with data to insert.\n\n        Keyword Args:\n            api_key (str): Your api-key.\n\n            project (str): Project name.\n\n        Returns:\n            An empty response.\n        '
    timeseries = []
    for depthseries in depthseries_with_datapoints:
        valueseries = TimeseriesWithDatapoints(depthseries.name, [])
        indexseries = TimeseriesWithDatapoints(_generateIndexName(depthseries.name), [])
        offset: int = 0
        for datapoint in depthseries.datapoints:
            valueseries.datapoints.append(Datapoint(offset, datapoint.value))
            indexseries.datapoints.append(Datapoint(offset, datapoint.depth))
            offset += MS_INCREMENT
        timeseries.append(valueseries)
        timeseries.append(indexseries)
    return ts.post_multi_tag_datapoints(timeseries)

def post_datapoints(name, depthdatapoints, **kwargs):
    'Insert a list of datapoints.\n\n    Args:\n        name (str):       Name of timeseries to insert to.\n\n        datapoints (list[v05.data_objects.Datapoint): List of datapoint data transfer objects to insert.\n\n    Keyword Args:\n        api_key (str): Your api-key.\n\n        project (str): Project name.\n\n    Returns:\n        An empty response.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    offset = 0
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries/data'.format(project))
    headers = {'api-key': api_key, 'content-type': 'application/json', 'accept': 'application/json'}
    datapoints = []
    depthpoints = []
    for datapoint in depthdatapoints:
        datapoints.append(Datapoint(offset, datapoint.value))
        depthpoints.append(Datapoint(offset, datapoint.depth))
        offset += MS_INCREMENT
    ul_dps_limit = 100000
    i = 0
    while (i < len(datapoints)):
        body = {'items': [{'name': name, 'datapoints': [dp.__dict__ for dp in datapoints[i:(i + ul_dps_limit)]]}, {'name': _generateIndexName(name), 'datapoints': [dp.__dict__ for dp in depthpoints[i:(i + ul_dps_limit)]]}]}
        _utils.post_request(url, body=body, headers=headers)
        i += ul_dps_limit
    return {}

def get_latest(name, **kwargs):
    'Returns a LatestDatapointObject containing the latest datapoint for the given depthseries.\n\n    Args:\n        name (str):       The name of the depthseries to retrieve data for.\n\n    Keyword Arguments:\n        api_key (str):          Your api-key.\n        project (str):          Project name.\n\n    Returns:\n        v05.data_objects.LatestDatapointsResponse: A data object containing the requested data with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries/latest/{}'.format(project, quote_plus(name)))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = _utils.get_request(url, headers=headers, cookies=config.get_cookies())
    return LatestDatapointResponse(res.json())

def get_depthseries(prefix=None, description=None, include_metadata=False, asset_id=None, path=None, **kwargs):
    'Returns a TimeSeriesObject containing the requested series.\n\n    Args:\n        prefix (str):           List timeseries with this prefix in the name.\n\n        description (str):      Filter timeseries taht contains this string in its description.\n\n        include_metadata (bool):    Decide if the metadata field should be returned or not. Defaults to False.\n\n        asset_id (int):        Get timeseries related to this asset.\n\n        path (str):             Get timeseries under this asset path branch.\n\n    Keyword Arguments:\n        limit (int):            Number of results to return.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n\n        autopaging (bool):      Whether or not to automatically page through results. If set to true, limit will be\n                                disregarded. Defaults to False.\n\n    Returns:\n        v05.data_objects.TimeSeriesResponse: A data object containing the requested timeseries with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries'.format(project))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    params = {'q': prefix, 'description': description, 'includeMetadata': include_metadata, 'assetId': asset_id, 'path': path, 'limit': (kwargs.get('limit', 10000) if (not kwargs.get('autopaging')) else 10000)}
    timeseries = []
    res = _utils.get_request(url=url, headers=headers, params=params, cookies=config.get_cookies())
    timeseries.extend([ts for ts in res.json()['data']['items']])
    next_cursor = res.json()['data'].get('nextCursor')
    while (next_cursor and kwargs.get('autopaging')):
        params['cursor'] = next_cursor
        res = _utils.get_request(url=url, headers=headers, params=params, cookies=config.get_cookies())
        timeseries.extend([ts for ts in res.json()['data']['items']])
        next_cursor = res.json()['data'].get('nextCursor')
    return TimeSeriesResponse({'data': {'nextCursor': next_cursor, 'previousCursor': res.json()['data'].get('previousCursor'), 'items': timeseries}})

def _generateIndexName(depthSeriesName):
    return (depthSeriesName + '_DepthIndex')

def _parse_exists_exception(exception):
    names: Set[str] = set()
    match = re.search('Some metrics already exist:\\s+(\\S+)(\\s|$)', exception)
    if match:
        names = set(re.split(',', match.group(1)))
    return names

def post_depth_series(depth_series, **kwargs):
    'Create a new depth series.\n\n        Args:\n            depth_series (list[v05.dto.TimeSeries]):   List of time series data transfer objects to create.\n            Corresponding depth series used for indexing will be created automatically, with unit of m(meter)\n\n        Keyword Args:\n            api_key (str): Your api-key.\n\n            project (str): Project name.\n        Returns:\n            An empty response.\n        '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries'.format(project))
    depth_indexes = copy.deepcopy(depth_series)
    for ts in depth_indexes:
        ts.name = _generateIndexName(ts.name)
        ts.unit = 'm'
        ts.isString = False
    body = {'items': [ts.__dict__ for ts in itertools.chain(depth_series, depth_indexes)]}
    headers = {'api-key': api_key, 'content-type': 'application/json', 'accept': 'application/json'}
    retry_list: Set(str) = set()
    try:
        _utils.post_request(url, body=body, headers=headers)
    except _utils.APIError as e:
        if ('Some metrics already exist' in str(e)):
            retry_list = _parse_exists_exception(str(e))
        else:
            raise e
    if (len(retry_list) > 0):
        body = {'items': [ts.__dict__ for ts in itertools.chain(depth_series, depth_indexes) if (ts.name in retry_list)]}
        try:
            _utils.post_request(url, body=body, headers=headers)
        except _utils.APIError as e:
            if ('Some metrics already exist' in str(e)):
                for ts in itertools.chain(depth_series, depth_indexes):
                    body = {'items': [ts.__dict__]}
                    try:
                        _utils.post_request(url, body=body, headers=headers)
                    except _utils.APIError as e:
                        if ('Some metrics already exist' in str(e)):
                            continue
                        else:
                            raise e
            else:
                raise e
    return {}

def _has_depth_index_changes(ds):
    if ((ds.metadata is None) and (ds.assetId is None) and (ds.description is None) and (ds.security_categories is None) and (ds.step is None)):
        return False
    return True

def update_depth_series(depth_series, **kwargs):
    'Update an existing time series.\n\n    For each field that can be updated, a null value indicates that nothing should be done.\n\n    Args:\n        depth_series (list[v05.dto.TimeSeries]):   List of time series data transfer objects to update.\n\n    Keyword Args:\n        api_key (str): Your api-key.\n\n        project (str): Project name.\n\n    Returns:\n        An empty response.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries'.format(project))
    body = {'items': [ts.__dict__ for ts in depth_series]}
    headers = {'api-key': api_key, 'content-type': 'application/json', 'accept': 'application/json'}
    res = _utils.put_request(url, body=body, headers=headers)
    if (res.json() == {}):
        for dsdto in depth_series:
            dsdto.name = _generateIndexName(dsdto.name)
            dsdto.isString = None
            dsdto.unit = None
        items = [ts.__dict__ for ts in depth_series if _has_depth_index_changes(ts)]
        body = {'items': items}
        if (len(items) > 0):
            res = _utils.put_request(url, body=body, headers=headers)
    return res.json()

def delete_depth_series(name, **kwargs):
    'Delete a depthseries.\n\n    Args:\n        name (str):   Name of depthseries to delete.\n\n    Keyword Args:\n        api_key (str): Your api-key.\n\n        project (str): Project name.\n\n    Returns:\n        An empty response.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries/{}'.format(project, name))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = _utils.delete_request(url, headers=headers)
    if (res.json() == {}):
        url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries/{}'.format(project, _generateIndexName(name)))
        res = _utils.delete_request(url, headers=headers)
    return res.json()

def reset_depth_series(name, **kwargs):
    'Delete all datapoints for a depthseries.\n\n       Args:\n           name (str):   Name of depthseries to delete.\n\n       Keyword Args:\n           api_key (str): Your api-key.\n\n           project (str): Project name.\n\n       Returns:\n           An empty response.\n       '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries/{}?timestampInclusiveBegin=0?timestampInclusiveEnd={}'.format(project, quote_plus(name), sys.maxsize))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = _utils.delete_request(url, headers=headers)
    if (res == {}):
        url = (config.get_base_url(api_version=0.5) + '/projects/{}/timeseries/{}?timestampInclusiveBegin=0?timestampInclusiveEnd={}'.format(project, quote_plus(_generateIndexName(name)), sys.maxsize))
        res = _utils.delete_request(url, headers=headers)
    return res.json()
