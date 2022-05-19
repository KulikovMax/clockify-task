import datetime
import json

from supporting_functions import get_tasks_api, get_api_key, extract_report

if __name__ == "__main__":
    api_key = get_api_key()
    tasks = get_tasks_api(api_key, headers={'Content-Type': 'application/json; charset=utf-8'})
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    report = extract_report(api_key, tasks, yesterday, datetime.datetime.today())
    print(report)

