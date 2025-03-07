"""
A tool that retrieves the image of a meme by its id. The original image and the image from the database are saved to the current directory.
"""


import requests
import base64
import asyncio
from sys import argv

api_url = "http://localhost:3000"


def get_url_content(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        print(response)
        return response.content
    except requests.exceptions.RequestException as e:
        return None

def create_meme(url: str, caption: str) -> dict:
    json = {
        "url": url,
        "caption": caption
    }
    response = requests.post(f"{api_url}/api/meme/", json=json)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    return response.json()

async def get_meme_by_id(id : int) -> dict:
    """Helper function that retrieves a meme by its id

    Args:
        id (int): The id of the meme

    Returns:
        dict: The response from the api
    """
    response = requests.get(f"{api_url}/api/meme/{id}")
    assert response.status_code == 200
    return response.json()

async def main():
    id : int = int(argv[1])
    response = await get_meme_by_id(id)

    encoded_image : str = response["data"]["image"]
    image_bytes = base64.b64decode(encoded_image)
    image_name = response["data"]["url"].split("/")[-1]

    original_image = get_url_content(response["data"]["url"])
    if original_image is None:
        print("Failed to fetch url content")
        exit(1)

    with open(f"original_{image_name}", "wb") as f:
        f.write(original_image)

    with open(f"{image_name}", "wb") as f:
        f.write(image_bytes)

    print("Image saved")

if __name__ == "__main__":
    asyncio.run(main())