import requests

from lib.helpers import get_config, setup_logger

logger = setup_logger()
config = get_config()

def grab_preview():
    url = f"http://{config['camera']['camDict']['0']['host']}:{config['camera']['camDict']['0']['port']}/api/capture_preview"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.content  # Return the image data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching capture preview: {e}")
        return None  # Return None or handle it as needed


def grab_capture(payload: dict):
    url = f"http://{config['camera']['camDict']['0']['host']}:{config['camera']['camDict']['0']['port']}/api/capture"

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.content  # Return the image data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching capture preview: {e}")
        return None  # Return None or handle it as needed
