# Clockify Task
This is my descision to Clockify API reading program.

## Install

 1. Install Python. More: https://www.python.org/downloads/
 2. Install PiP. More: https://pip.pypa.io/en/stable/cli/pip_install/
 3. Install requests package: `pip install requests`

## API Key Generation

 1. Go to Clockify: clockify.me
 2. Go to Profile Settings
 3. Generate an API key

## Program Usage

 1. Download or clone clockify-task program: https://github.com/KulikovMax/clockify-task
 2. Go to your IDE
 3. (optional). Set your API key as environment variable.
 4. Run 'main.py'
 5. (if you set API key as environment variable) Follow instructions on the terminal
 6. (if you did not set API key as environment variable) Copy your API key and paste it to console when program asks you. Than follow instructions on the terminal.

## Supporting Functions Description

***get_api_key()***
`get_api_key() -> str` 
Receive API key from environment variable. If    not founded, asks user to ender `API_KEY` to the terminal.  Calls    `check_api_key()` function. If check is OK, returns `API_KEY`. If check    returned error, calls itself until user won't finish program    execution or until user provides correct `API_KEY`.

***check_api_key()***

    check_api_key(api_key: str) -> str

Makes HTTP request to https://api.clockify.me/api/v1/user. If `API_KEY` is OK, prints message "OK" and returns string "OK". If there is an error during request, shows error message with description and returns "Error".

   
***make_request()***
  

      make_request(to_receive: str, headers: dict, params: dict = None, selected_workspace: int = 0, selected_project: int = 0, resp: Response = None) -> Response or None

Creates data for passing to `requests.Request` object. Generates request based on this data. Required params are `to_receive` and `headers`.  `to_recieve` describes options that we need to extract from Clockify: 

 - workspaces
 - projects
 - tasks

  `headers` are HTTP request headers. You will allways need to pass at least `'x-api-key': API_KEY`.
  For each option in `to_recieve` function creates its own url. 
  **IMPORTANT**
  If you need to recieve `projects` or `tasks`, you will need to pass requests.Response object, that contains `request url`of the previous request. For example, we need to extract `projects`:

     
    workspace_resp = make_request('workspaces', headers)  # Making request to receive workspaces data 
    workspaces = workspace_resp.json() # Making JSON from received data
    selected_workspace = int(input('Enter number of workspace: ')) # Asking user to choose wokspace
    project_resp = make_request('projects', headers, resp=workspace_resp, selected_workspace=selected_workspace) # Passing previous response

***get_api_tasks()***

    get_api_tasks(api_key: str, headers: dict = None, params: dict = None) -> dict
Main function to receive tasks. It calls `make_request()`to workspace, project and tasks. Than it returns tasks at JSON format. 

***extract_report()***

    extract_report(api_key: str, data: dict, date_start: datetime, date_end: datetime) -> str
Extracts report from the Clockify API.  All parameters are required. Exctracts report about project previously selected by user.  After retrieving data calls `prettify_report()`. After prettifying returns report string.
***prettify_report()***

    prettify_report(data: dict) -> str
Makes from received in `extract_report()` JSON pretty formated string with raport.