
from supporting_functions import check_api_key, get_tasks_api, get_api_key

if __name__ == "__main__":
    api_key = get_api_key()
    tasks = get_tasks_api(api_key, headers={'Content-Type': 'application/json; charset=utf-8'})

