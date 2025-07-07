import requests


def get_photo_from_pexels(
        api_key: str,
        keyword: str,
        photo_path: str
    ) -> None:

    headers = {
        "Authorization": api_key
    }

    image_url = None

    response = requests.get(f"https://api.pexels.com/v1/search?query={keyword}&per_page=1", headers = headers)
    if response.status_code == 200:
        data = response.json()
        if data["total_results"] > 0:
            image_url = data["photos"][0]["src"]["original"]
    if image_url:
        with open(photo_path, "wb") as f:
            f.write(
                requests.get(image_url).content
            )