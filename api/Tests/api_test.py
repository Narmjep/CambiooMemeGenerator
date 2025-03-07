import requests
import pytest
import json
from src.pg import destroy_db, create_table, init_connection, close_connection
import httpx
import random
import hashlib
import base64

api_url = "http://localhost:3000"

example_image_url = "https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif"


# ------------------------------------ #
#          Helper functions            #
# ------------------------------------ #

async def create_meme(url: str, caption: str) -> dict:
    """Helper function that creates a meme sends it to the api

    Args:
        url (str): A url to an image
        caption (str): A caption

    Returns:
        dict: The response from the api
    """

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

async def createTestMemes(size : int) -> list:
    """Creates a number of test memes and sends them to the api

    Args:
        size (int): The number of memes to create

    Returns:
        list: A list of captions for the memes
    """

    captions = []
    for i in range(size):
        captions.append(f"Caption {i}")
        await create_meme(example_image_url, captions[i])
    return captions

# ------------------------------------ #
#    Meme creation and retrieval       #
# ------------------------------------ #


@pytest.mark.asyncio
async def test_create_meme():
    """Tests the '/api/meme/' endpoint by creating a meme
    """

    await init_connection()
    await destroy_db()
    await create_table()
    assert create_meme(example_image_url, "Cat")
    await close_connection()

@pytest.mark.asyncio
async def test_create_meme_invalid_url():
    """Tests the '/api/meme/' endpoint by creating a meme with an invalid url
    """

    await init_connection()
    await destroy_db()
    await create_table()
    response = requests.post(f"{api_url}/api/meme/", json={"url": "invalid_url", "caption": "Cat"})
    assert response.status_code == 200
    assert response.json()["status"] == "error"
    await close_connection()


    

@pytest.mark.asyncio
async def test_get_meme_by_id():
    """Tests the '/api/meme/{id}' endpoint by creating a meme and then retrieving it
    """

    await init_connection()
    await destroy_db()
    await create_table()
    await test_create_meme()
    
    await create_meme(example_image_url, "Cat")
    
    response = requests.get(f"{api_url}/api/meme/1")
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "success"
    assert json["data"]["caption"] == "Cat"
    await close_connection()

@pytest.mark.asyncio
async def test_get_nonexistent_meme():
    """Tests the '/api/meme/{id}' endpoint by trying to retrieve a meme that does not exist
    """

    await init_connection()
    await destroy_db()
    await create_table()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/meme/1")
    
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "error"
    await close_connection()

# Image

@pytest.mark.asyncio
async def test_image_integrity():
    """Tests the integrity of the image data stored in the database by comparing the hash of the original image with the hash of the stored image
    """

    await init_connection()
    await destroy_db()
    await create_table()

    await create_meme(example_image_url, "Cat")

    original_image = requests.get(example_image_url).content
    assert original_image is not None

    original_hash = hashlib.md5(original_image).hexdigest()

    res = await get_meme_by_id(1)
    assert res["status"] == "success"  
    assert res["data"]["image"] is not None
    encoded_img = res["data"]["image"]
    image_bytes = base64.b64decode(encoded_img)

    hash_stored_image = hashlib.md5(image_bytes).hexdigest()

    assert original_hash == hash_stored_image

    await close_connection()

# ------------------------------------ #
#              Votes                   #
# ------------------------------------ #

@pytest.mark.asyncio
async def test_upvote_meme():
    """Tests the '/api/meme/{id}/vote/' endpoint by creating a meme, upvoting it and then retrieving it to check the upvotes
    """

    await init_connection()
    await destroy_db()
    await create_table()


    await create_meme(example_image_url, "Cat")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/meme/1/vote/")
    
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "success"
    res = await get_meme_by_id(1)
    assert res["data"]["upvotes"] == 1
    await close_connection()

@pytest.mark.asyncio
async def test_multiple_upvotes():
    """Tests the '/api/meme/{id}/vote/' endpoint by creating a meme, upvoting it multiple times and then retrieving it to check the upvotes
    """

    await init_connection()
    await destroy_db()
    await create_table()

    await create_meme(example_image_url, "Cat")

    for i in range(10):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_url}/api/meme/1/vote/")
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    res = await get_meme_by_id(1)
    assert res["data"]["upvotes"] == 10

    await close_connection()

@pytest.mark.asyncio
async def test_upvote_nonexistent_meme():
    """Tests the '/api/meme/{id}/vote/' endpoint by trying to upvote a meme that does not exist
    """

    await init_connection()
    await destroy_db()
    await create_table()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/meme/1/vote/")
    
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "error"
    assert json["error"] == "Meme not found"
    await close_connection()


# Top 10

@pytest.mark.asyncio
async def test_get_top_memes():
    """Tests the '/api/top/' endpoint by creating 16 memes, upvoting the first 10 and then retrieving the top 10
    """

    await init_connection()
    await destroy_db()
    await create_table()

    print("-------------------------------------")
    # Create 16 memes
    captions = await createTestMemes(16)

    # Upvote the first 10
    for i in range(16):
        for j in range(i):
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{api_url}/api/meme/{i+1}/vote/")
                assert response.status_code == 200
                assert response.json()["status"] == "success"

    # Get top 10
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/top/")
        assert response.status_code == 200
        json = response.json()
        assert json["status"] == "success"
        data = json["data"]
        assert len(data) == 10
        for i in range(10):
            # Number one should be the last one
            assert data[i]["caption"] == captions[15-i]

    await close_connection()

@pytest.mark.asyncio
async def test_get_top_memes_empty_db():
    """Tests the '/api/top/' endpoint by trying to retrieve the top 10 memes from an empty database
    """

    await init_connection()
    await destroy_db()
    await create_table()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/top/")
        assert response.status_code == 200
        json = response.json()
        assert json["status"] == "success"
        data = json["data"]
        assert len(data) == 0

    await close_connection()

# Random

@pytest.mark.asyncio
async def test_get_random_meme():
    """Tests the '/api/meme/random/' endpoint by creating 10 memes and then retrieving a random one
    """

    await init_connection()
    await destroy_db()
    await create_table()

    captions = await createTestMemes(10)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/meme/random/")
        assert response.status_code == 200
        json = response.json()
        assert json["status"] == "success"
        data = json["data"]
        assert data["caption"] in captions

    await close_connection()

