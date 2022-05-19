from requests import request, exceptions, Response
from os import environ
from constants import BASE_URL, URLS_DICT, CHECK_ERROR_MESSAGE, CHECK_SUCCESS_MESSAGE
import json


def get_api_key() -> str:
    """
    Extracts API KEY from environment variable or through user input. Than checks it. If checking was unsuccessful,
        prints message and calls itself again.
    :return: api_key
    """
    api_key = environ.get('API_KEY')
    if api_key is None:
        api_key = input("Enter your API KEY here: ")

    check_result = check_api_key(api_key)
    print(f'*API KEY check: {check_result}')

    if check_result == 'OK':
        print(CHECK_SUCCESS_MESSAGE)
        return api_key
    else:
        print(CHECK_ERROR_MESSAGE)
        get_api_key()


def check_api_key(api_key: str) -> str:
    """
    Checks API KEY by making request to Clockify API. If response returns an Error, than print error message.
    :param api_key: str. API KEY for Clockify API
    :return: str 'OK' or 'Error'
    """
    try:
        req = request(method='GET', url=BASE_URL + URLS_DICT['user'], headers={'x-api-key': api_key})
        req.raise_for_status()
        return 'OK'
    except exceptions.HTTPError as error:
        if error.response.status_code == 401:
            print('You are unauthorized. Check your API KEY. It might be expired or missing characters.')
            return 'Error'
    except exceptions.InvalidHeader:
        print('Check that your API KEY is right format')
        return 'Error'


def make_request(to_receive: str, headers: dict, params: dict = None, selected_workspace: int = 0,
                 selected_project: int = 0, resp: Response = None) -> Response or None:
    """
    Generates request to the Clockify API according to what you need to receive.
    Returns None if you try to receive something unexpected.
    Returns Response object if everything went smooth.

    :param to_receive: Can be 'workspaces', 'projects' or 'tasks'. Describes what you need to get from API.
    :param headers: HTTP-request headers.
    :param params: optional. HTTP-request params.
    :param resp: optional. requests.Response object that contains data needed for extracting next API level.
    :param selected_workspace: optional. If you have several workspaces on Clockify, choose tha one you need.
    :param selected_project: optional. If you have several projects on Clockify, choose tha one you need.
    :return: requests.Response or None
    """

    receive_possibilities = ['workspaces', 'projects', 'tasks']
    if to_receive not in receive_possibilities:
        print('Receive Possibilities are:\nworkspaces;\nprojects;\ntasks.')
        return None

    if to_receive == 'workspaces':
        url = BASE_URL + URLS_DICT['workspaces']
        print('Receiving workspaces...')
    elif to_receive == 'projects':
        url = resp.url.split('?')[0] + resp.json()[selected_workspace]['id'] + '/projects/'
        print('Receiving projects...')
    else:
        url = resp.url.split('?')[0] + resp.json()[selected_project]['id'] + '/tasks/'
        print('Receiving tasks...')

    return request(method='GET', url=url, headers=headers, params=params)


def get_tasks_api(api_key: str, headers: dict = None, params: dict = None) -> list:
    """
    Gets tasks from Clockify API. Makes 3 request, each on different API levels, to receive all data required to
        extract tasks API. Work Flow:
            -->> Make request to workspaces. Returns JSON with all current Workspaces data.
            -->> Ask user to select workspace.
            -->> Make request to projects (passing selected workspace_id). Returns JSON with all current projects data.
            -->> Ask user to select project.
            -->> Make request to tasks (passing selected project_id). Returns JSON with selected project tasks data.

    :param api_key: Clockify API KEY
    :param headers: optional. HTTP-request headers.
    :param params: optional. HTTP-request params.
    :return: list (Tasks JSON)
    """
    if headers is None:
        headers = {'x-api-key': api_key}
    else:
        headers.update({'x-api-key': api_key})

    if params is None:
        params = {'hydrated': True}
    else:
        params.update({'hydrated': True})

    # Making request to receive workspaces data
    workspace_resp = make_request('workspaces', headers)
    workspaces = workspace_resp.json()
    # Output all available workspaces and let user choose the one needed.
    for i in range(0, len(workspaces)):
        print(f"{i} --- {workspaces[i]['name']}")
    selected_workspace = int(input('Enter number of workspace: '))

    # Making request to receive projects data
    project_resp = make_request('projects', headers, resp=workspace_resp, selected_workspace=selected_workspace)
    projects = project_resp.json()
    # Output all available projects and let user choose the one needed.
    for i in range(0, len(projects)):
        print(f"{i} --- {projects[i]['name']}")
    selected_project = int(input('Enter number of project: '))
    print(f"You selected: {projects[selected_project]['name']}")

    # Making request to receive tasks
    tasks_resp = make_request('tasks', headers, params, resp=project_resp, selected_project=selected_project)
    tasks_string = json.dumps(tasks_resp.json(), ensure_ascii=False, indent=4).encode('utf-8')
    tasks = json.loads(tasks_string)
    return tasks
