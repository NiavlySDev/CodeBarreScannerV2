import requests

def get_data(number):
    url = f"https://world.openfoodfacts.org/api/v2/product/{number}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return None