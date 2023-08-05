
'Cloud Storage Module\n\nThis module mirrors the Cloud Storage API. It allows you to manage files in cloud storage.\n\nhttps://doc.cognitedata.com/0.4/#Cognite-API-Cloud-Storage\n'
import os
import warnings
import requests
import cognite._utils as _utils
import cognite.config as config
from cognite.v04.dto import FileInfoResponse, FileListResponse

def upload_file(file_name, file_path=None, directory=None, source=None, file_type=None, content_type=None, **kwargs):
    'Upload metadata about a file and get an upload link.\n\n    The link will expire after 30 seconds if not resumable. A resumable upload link is default. Such a link is one-time\n    use and expires after one week. For more information, check this link:\n    https://cloud.google.com/storage/docs/json_api/v1/how-tos/resumable-upload. Use PUT request to upload file with the\n    link returned.\n\n    If file_path is specified, the file will be uploaded directly by the SDK.\n\n    Args:\n        file_name (str):      File name. Max length is 256.\n\n        file_path (str, optional):     Path of file to upload, if omitted a upload link will be returned.\n\n        content_type (str, optional):   MIME type of your file. Required if file_path is specified.\n\n        directory (str, optional):      Directory containing the file. Max length is 512.\n\n        source (str, optional):         Source that this file comes from. Max length is 256.\n\n        file_type (str, optional):      File type. E.g. pdf, css, spreadsheet, .. Max length is 64.\n\n    Keyword Args:\n        api_key (str, optional):        Your api-key.\n\n        project (str, optional):        Project name.\n\n        metadata (dict):      Customized data about the file.\n\n        tag_ids (list):       IDs (tagIds) of equipment related to this file.\n\n        resumable (bool):     Whether to generate a resumable URL or not. Default is true.\n\n        overwrite (bool):     Whether to overwrite existing data if duplicate or not. Default is false.\n\n    Returns:\n        dict: A dictionary containing the field fileId and optionally also uploadURL if file_path is omitted.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.4) + '/projects/{}/storage/metadata'.format(project))
    headers = {'api-key': api_key, 'content-type': 'application/json', 'accept': 'application/json', 'X-Upload-Content-Type': content_type}
    params = {'resumable': kwargs.get('resumable', True), 'overwrite': kwargs.get('overwrite', False)}
    body = {'fileName': file_name, 'directory': directory, 'source': source, 'fileType': file_type, 'metadata': kwargs.get('metadata', None), 'tagIds': kwargs.get('tagIds', None)}
    res_storage = _utils.post_request(url=url, body=body, headers=headers, params=params, cookies=config.get_cookies())
    result = res_storage.json()['data']
    if file_path:
        if (not content_type):
            warning = 'content_type should be specified when directly uploading the file.'
            warnings.warn(warning)
        headers = {'content-length': str(os.path.getsize(file_path))}
        with open(file_path, 'rb') as file:
            requests.put(result['uploadURL'], data=file, headers=headers)
        result.pop('uploadURL')
    return result

def download_file(id, get_contents=False, **kwargs):
    'Get list of files matching query.\n\n    Args:\n        id (int):                           Path to file to upload, if omitted a upload link will be returned.\n\n        get_contents (bool, optional):      Boolean to determince whether or not to return file contents as string.\n                                            Default is False and download url is returned.\n\n    Keyword Args:\n        api_key (str, optional):            Your api-key.\n\n        project (str, optional):            Project name.\n\n    Returns:\n        str: Download link if get_contents is False else file contents.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.4) + '/projects/{}/storage/{}'.format(project, id))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = _utils.get_request(url=url, headers=headers, cookies=config.get_cookies())
    if get_contents:
        dl_link = res.json()['data']
        res = requests.get(dl_link)
        return res.content
    return res.json()['data']

def delete_files(file_ids, **kwargs):
    'Delete\n\n    Args:\n        file_ids (list[int]):   List of IDs of files to delete.\n\n    Keyword Args:\n        api_key (str):          Your api key.\n\n        project (str):          Your project.\n\n    Returns:\n        list: List of files deleted and files that failed to delete.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.4) + '/projects/{}/storage/delete'.format(project))
    headers = {'api-key': api_key, 'content-type': 'application/json', 'accept': 'application/json'}
    body = {'items': file_ids}
    res = _utils.post_request(url, body=body, headers=headers)
    return res.json()['data']

def list_files(name=None, directory=None, file_type=None, source=None, **kwargs):
    "Get list of files matching query.\n\n    Args:\n        name (str, optional):      List all files with this name.\n\n        directory (str, optional):      Directory to list files from.\n\n        source (str, optional):         List files coming from this source.\n\n        file_type (str, optional):      Type of files to list.\n\n    Keyword Args:\n        api_key (str, optional):        Your api-key.\n\n        project (str, optional):        Project name.\n\n        tag_id (list):                  Returns all files associated with this tagId.\n\n        sort (str):                     Sort descending or ascending. 'ASC' or 'DESC'.\n\n        limit (int):                    Number of results to return.\n\n        autopaging (bool):              Whether or not to automatically page through results. If set to true, limit will be\n                                        disregarded. Defaults to False.\n\n    Returns:\n        v04.dto.FileListResponse: A data object containing the requested files information.\n    "
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.4) + '/projects/{}/storage'.format(project))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    params = {'tagId': kwargs.get('tag_id', None), 'dir': directory, 'name': name, 'type': file_type, 'source': source, 'isUploaded': kwargs.get('is_uploaded', None), 'sort': kwargs.get('sort', None), 'limit': (kwargs.get('limit', 100) if (not kwargs.get('autopaging')) else 10000)}
    file_list = []
    res = _utils.get_request(url=url, headers=headers, params=params, cookies=config.get_cookies())
    file_list.extend(res.json()['data']['items'])
    next_cursor = res.json()['data'].get('nextCursor', None)
    while (next_cursor and kwargs.get('autopaging')):
        params['cursor'] = next_cursor
        res = _utils.get_request(url=url, headers=headers, params=params, cookies=config.get_cookies())
        file_list.extend(res.json()['data']['items'])
        next_cursor = res.json()['data'].get('nextCursor', None)
    return FileListResponse({'data': {'nextCursor': next_cursor, 'previousCursor': res.json()['data'].get('previousCursor'), 'items': file_list}})

def get_file_info(id, **kwargs):
    'Returns information about a file.\n\n    Args:\n        id (int):                   Id of the file.\n\n    Keyword Args:\n        api_key (str, optional):    Your api-key.\n\n        project (str, optional):    Project name.\n\n    Returns:\n        v04.dto.FileInfoResponse: A data object containing the requested file information.\n    '
    (api_key, project) = config.get_config_variables(kwargs.get('api_key'), kwargs.get('project'))
    url = (config.get_base_url(api_version=0.4) + '/projects/{}/storage/{}/info'.format(project, id))
    headers = {'api-key': api_key, 'accept': 'application/json'}
    res = _utils.get_request(url, headers=headers)
    return FileInfoResponse(res.json())
