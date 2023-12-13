import requests

# Configuration
GRAFANA_URL = 'https://YOUR_GRAFANA_URL'
COOKIE_VALUE = 'YOUR_COOKIE_VALUE'
HEADERS = {
    "Cookie": f"grafana_sess={COOKIE_VALUE}"
}


def list_all_dashboards():
    response = requests.get(f"{GRAFANA_URL}/api/search", headers=HEADERS)
    response.raise_for_status()
    return response.json()


def download_dashboard(uid):
    response = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=HEADERS)
    response.raise_for_status()
    return response.json()


def main():
    dashboards = list_all_dashboards()
    for dashboard in dashboards:
        if dashboard["type"] == "dashboard":
            uid = dashboard["uid"]
            data = download_dashboard(uid)
            title = dashboard["title"].replace(" ", "-").lower()  # Convert title to lowercase and replace spaces with hyphens
            filename = f"{title}-{uid}.json"
            with open(filename, "w") as f:
                f.write(requests.utils.json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
