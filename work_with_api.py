import requests
import env


def get_faceit_stat_by_nicknsame(nickname: str):
    auth_header = f"Bearer {env.FACEIT_API_KEY}"
    headers = {"Authorization": auth_header}
    url = f"https://open.faceit.com/data/v4/players?nickname={nickname}"
    response = requests.get(url, headers=headers)

    return response.json()
