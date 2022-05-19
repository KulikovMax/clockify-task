from datetime import datetime, timedelta

from requests import request, exceptions, Response
from os import environ
from constants import BASE_URL, URLS_DICT, CHECK_ERROR_MESSAGE, CHECK_SUCCESS_MESSAGE, REPORTS_BASE_URL
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
        url = resp.url.split('?')[0] + resp.json()[selected_project]['id']
        print('Receiving tasks...')

    return request(method='GET', url=url, headers=headers, params=params)


def get_api_tasks(api_key: str, headers: dict = None, params: dict = None) -> dict:
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
    :return: dict (Tasks JSON)
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
    tasks = tasks_resp.json()
    return tasks


def extract_report(api_key: str, data: dict, date_start: datetime, date_end: datetime) -> str:
    """
    Extracts Report on selected project from Reports Clockify API.
    :param api_key: Clockify API key.
    :param data: JSON from Clockify API. Should content workspaceId and projectId.
    :param date_start: start of the period that we need report about
    :param date_end: end of the period that we need report about
    :return: str with Report
    """
    print('Extracting Summary Report...')
    # receiving data from passed argument that we need to pass to HTTP request
    workspace_id = data['workspaceId']
    project_id = data['id']

    # building HTTP request parts
    report_url = REPORTS_BASE_URL + f'workspaces/{workspace_id}/reports/summary'
    report_body = json.dumps({"dateRangeStart": date_start.isoformat('T'),
                              "dateRangeEnd": date_end.isoformat('T'),
                              "summaryFilter": {
                                  "groups": [
                                      "PROJECT",
                                      "DATE",
                                      "TASK"
                                  ]
                              },
                              "projects": {
                                  "ids": [str(project_id)]},
                              })
    headers = {'x-api-key': api_key, 'Content-type': 'application/json'}

    req = request(method='POST', url=report_url, headers=headers, data=report_body)
    report_json = req.json()
    print('Extraction finished...')

    report = prettify_report(report_json)
    return report


def prettify_report(data: dict) -> str:
    """
    Makes pretty txt Report from received data from Clockify API.
    :param data: data that needs to be prettified. Must be JSON from reports.api.clockify.me
    :return:str with prettified report
    """
    # Retrieving data that we need to operate with
    group_one = data.get('groupOne')[0]
    print('Prettifying Report...')
    duration = timedelta(seconds=group_one['duration'])
    grouped_dates = group_one['children']

    # retrieve dates and tasks with duration and parse it to string
    time_periods = ''
    for date in grouped_dates:
        date_str = '--->' + date['name'] + '\n-----------------------------------\n'
        for task in date['children']:
            unformatted_time_spent = task['duration']
            time_spent = str(timedelta(seconds=unformatted_time_spent))
            date_str += f'Task: {task["name"]}\nDuration: {time_spent}\n' + '-----------------------------------\n'
        time_periods += date_str + '\n'

        # building report
    report = \
        f"""
+++++++++   SUMMARY REPORT   +++++++++
Project name: {group_one['name']}
Project Clockify Id: {group_one['_id']}
Total Duration: {duration}
Working Periods:
-----------------------------------
{time_periods}"""
    return report
