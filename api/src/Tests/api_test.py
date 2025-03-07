import requests
import pytest
import json
from ..pg import destroy_db, create_table, init_connection, close_connection
import httpx
import random

api_url = "http://localhost:3000"

# Creation


async def create_meme(url: str, caption: str) -> dict:
    json = {
        "url": url,
        "caption": caption
    }
    response = requests.post(f"{api_url}/api/meme/", json=json)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    return response.json()

@pytest.mark.asyncio
async def test_create_meme():
    await init_connection()
    await destroy_db()
    await create_table()
    assert create_meme("https://www.google.com", "Cat")
    await close_connection()


async def get_meme_by_id(id : int) -> dict:
    response = requests.get(f"{api_url}/api/meme/{id}")
    assert response.status_code == 200
    return response.json()
    

@pytest.mark.asyncio
async def test_get_meme_by_id():
    await init_connection()
    await destroy_db()
    await create_table()
    await test_create_meme()
    
    await create_meme("https://www.google.com", "Cat")
    
    response = requests.get(f"{api_url}/api/meme/1")
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "success"
    assert json["data"]["caption"] == "Cat"
    await close_connection()

@pytest.mark.asyncio
async def test_get_nonexistent_meme():
    await init_connection()
    await destroy_db()
    await create_table()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/meme/1")
    
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "error"
    await close_connection()


# Upvoting

@pytest.mark.asyncio
async def test_upvote_meme():
    await init_connection()
    await destroy_db()
    await create_table()


    await create_meme("https://www.google.com", "Cat")

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
    await init_connection()
    await destroy_db()
    await create_table()

    await create_meme("https://www.google.com", "Cat")

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

async def createTestMemes(size : int) -> tuple:
    urls =[]
    captions = []
    for i in range(size):
        urls.append(f"https://{i}.com")
        captions.append(f"Caption {i}")
        await create_meme(urls[i], captions[i])
    return urls, captions

@pytest.mark.asyncio
async def test_get_top_memes():
    await init_connection()
    await destroy_db()
    await create_table()

    print("-------------------------------------")
    # Create 16 memes
    urls, captions = await createTestMemes(16)

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
            assert data[i]["url"] == urls[15-i]

    await close_connection()

@pytest.mark.asyncio
async def test_get_top_memes_empty_db():
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
    await init_connection()
    await destroy_db()
    await create_table()

    urls, captions = await createTestMemes(10)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_url}/api/meme/random/")
        assert response.status_code == 200
        json = response.json()
        assert json["status"] == "success"
        data = json["data"]
        assert data["caption"] in captions
        assert data["url"] in urls

    await close_connection()

