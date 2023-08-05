
'Assets Module.\n\nThis module mirrors the Assets API.\n\nhttps://doc.cognitedata.com/0.5/#Cognite-API-Assets\n'
import cognite._constants as constants
import cognite._utils as utils
import cognite.config as config
from cognite.v05.dto import AssetResponse, AssetListResponse, Asset

def get_assets(name=None, path=None, description=None, metadata=None, depth=None, fuzziness=None, **kwargs):
    'Returns assets matching provided description.\n\n    Args:\n        name (str):             The name of the asset(s) to get.\n\n        path (str):             The path of the subtree to search in.\n\n        description (str):      Search query.\n\n        metadata (str):         The metadata values used to filter the results.\n\n        depth (int):            Get sub assets up oto this many levels below the specified path.\n\n        fuzziness (int):        The degree of fuzziness in the name matching.\n\n    Keyword Arguments:\n        limit (int):            The maximum number of assets to be returned.\n\n        cursor (str):           Cursor to use for paging through results.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n    Returns:\n        v05.dto.AssetResponse: A data object containing the requested assets with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/assets'.format(project))
    params = {'name': name, 'description': description, 'path': path, 'metadata': metadata, 'depth': depth, 'fuzziness': fuzziness, 'cursor': kwargs.get('cursor'), 'limit': kwargs.get('limit', constants.LIMIT)}
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = utils.get_request(url, params=params, headers=headers, cookies=config.get_cookies())
    return AssetListResponse(res.json())

def get_asset(asset_id, **kwargs):
    'Returns the asset with the provided assetId.\n\n    Args:\n        asset_id (int):         The asset id of the top asset to get.\n\n    Keyword Arguments:\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n    Returns:\n        v05.dto.AssetResponse: A data object containing the requested assets with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/assets/{}/subtree'.format(project, asset_id))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = utils.get_request(url, headers=headers, cookies=config.get_cookies())
    return AssetResponse(res.json())

def get_asset_subtree(asset_id, depth=None, **kwargs):
    'Returns asset subtree of asset with provided assetId.\n\n    Args:\n        asset_id (int):         The asset id of the top asset to get.\n\n        depth (int):            Get subassets this many levels below the top asset.\n\n    Keyword Arguments:\n        limit (int):            The maximum nuber of assets to be returned.\n\n        cursor (str):           Cursor to use for paging through results.\n\n        api_key (str):          Your api-key.\n\n        project (str):          Project name.\n    Returns:\n        v05.dto.AssetResponse: A data object containing the requested assets with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/assets/{}/subtree'.format(project, asset_id))
    params = {'depth': depth, 'limit': kwargs.get('limit', constants.LIMIT), 'cursor': kwargs.get('cursor')}
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = utils.get_request(url, params=params, headers=headers, cookies=config.get_cookies())
    return AssetListResponse(res.json())

def post_assets(assets, **kwargs):
    'Insert a list of assets.\n\n    Args:\n        assets (list[v05.dto.Asset]): List of asset data transfer objects.\n\n    Keyword Args:\n        api_key (str): Your api-key.\n\n        project (str): Project name.\n\n    Returns:\n        v05.dto.AssetResponse: A data object containing the posted assets with several getter methods with different\n        output formats.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/assets'.format(project))
    body = {'items': [asset.__dict__ for asset in assets]}
    headers = {'api-key': api_key, 'content-type': 'application/json', 'accept': 'application/json'}
    res = utils.post_request(url, body=body, headers=headers, cookies=config.get_cookies())
    return AssetListResponse(res.json())

def delete_assets(asset_ids, **kwargs):
    'Delete a list of assets.\n\n    Args:\n        asset_ids (list[int]): List of IDs of assets to delete.\n\n    Keyword Args:\n        api_key (str): Your api-key.\n\n        project (str): Project name.\n\n    Returns:\n        An empty response.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.5) + '/projects/{}/assets/delete'.format(project))
    body = {'items': asset_ids}
    headers = {'api-key': api_key, 'content-type': 'application/json', 'accept': 'application/json'}
    res = utils.post_request(url, body=body, headers=headers, cookies=config.get_cookies())
    return res.json()
