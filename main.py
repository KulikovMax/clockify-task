from datetime import datetime, timedelta, time

from supporting_functions import get_tasks_api, get_api_key, extract_report

if __name__ == "__main__":
    api_key = get_api_key()
    tasks = get_tasks_api(api_key, headers={'Content-Type': 'application/json; charset=utf-8'})
    yesterday = datetime.combine(datetime.today() - timedelta(days=1), time.min)
    report = extract_report(api_key, tasks, yesterday, datetime.today())
    print(report)
