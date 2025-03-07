import requests
import base64

api_url = "http://localhost:3000"
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cat_August_2010-4.jpg/1200px-Cat_August_2010-4.jpg"

def get_url_content(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        print(response)
        return response.content
    except requests.exceptions.RequestException as e:
        return None
    
with open("original.jpg", "wb") as f:
    content = get_url_content(image_url)
    if content is None:
        print("Failed to fetch url content")
        exit(1)
    f.write(content)




def create_meme(url: str, caption: str) -> dict:
    json = {
        "url": url,
        "caption": caption
    }
    response = requests.post(f"{api_url}/api/meme/", json=json)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    return response.json()

create_meme(image_url, "Cat")

url = "http://localhost:3000/api/meme/random/"

response = requests.get(url)

assert response.status_code == 200
assert response.json()["status"] == "success"
assert len(response.json()["data"]) > 0

encoded_image : str = response.json()["data"]["image"]
image_bytes = base64.b64decode(encoded_image)

image_name = response.json()["data"]["url"].split("/")[-1]

with open(f"{image_name}", "wb") as f:
    f.write(image_bytes)

print("Image saved")