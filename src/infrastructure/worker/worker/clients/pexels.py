from ..settings import settings

import requests
from celery.utils.log import get_logger


logger = get_logger(__name__)


class PexelsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_photo(
            self ,
            keyword: str,
            photo_path: str
        ) -> None:
        logger.info(f"Searching for photo with keyword: {keyword}")

        image_url = None
        headers = {"Authorization": self.api_key}
        response = requests.get(f"https://api.pexels.com/v1/search?query={keyword}&per_page=1", headers = headers)

        if response.status_code == 200:
            data = response.json()

            logger.info(f"Received response from Pexels. Number of results: {data['total_results']}")
            if data["total_results"] > 0:
                image_url = data["photos"][0]["src"]["original"]

                logger.info(f"Downloading photo from URL: {image_url}")
                with open(photo_path, "wb") as f:
                    f.write(
                        requests.get(image_url).content
                    )
            else:
                logger.warning(f"No results found for keyword: {keyword}")
        else:
            logger.error(f"Failed to fetch photo from Pexels. Status code: {response.status_code}, Response: {response.text}")

def get_pexels_client(api_key: str = settings.PEXELS_API_KEY) -> PexelsClient:
    return PexelsClient(api_key)