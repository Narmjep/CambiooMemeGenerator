import pg as pg
from fastapi import FastAPI
from pydantic import BaseModel
import json
import requests
import base64

app = FastAPI()

class MemeCreationData(BaseModel):
    url: str
    caption: str

class MemeResponseData(BaseModel):
    id: int
    url: str
    caption: str
    upvotes: int
    image: str

def createSuccessResponse(data=None):
    if data is None:
        return {"status": "success"}
    return {"status": "success", "data": data}

def createErrorResponse(error):
    return {"status": "error", "error": error}


def get_url_content(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.content
    except requests.exceptions.RequestException as e:
        return None

@app.post("/api/meme/")
async def create_meme(meme: MemeCreationData):
    content = get_url_content(meme.url)
    if content is None:
        return createErrorResponse("Failed to fetch url content")
    
    encoded_img = base64.b64encode(content).decode("utf-8")

    await pg.create_meme(meme.url, meme.caption, encoded_img)
    return {"status": "success"}

@app.get("/api/meme/{id}")
async def get_meme_by_id(id: int):
    meme = await pg.get_meme_by_id(id)
    if meme is None:
        return createErrorResponse("Meme not found")
    return createSuccessResponse(MemeResponseData(
        id=meme.id,
        url=meme.url,
        caption=meme.caption,
        upvotes=meme.upvotes,
        image=meme.image
        )
    )

@app.get("/api/meme/{id}/vote/")
async def upvote_meme(id: int):
    res = await pg.upvote_meme(id)
    if not res:
        return createErrorResponse("Meme not found")
    return createSuccessResponse()

@app.get("/api/top/")
async def get_top_memes():
    memes = await pg.get_top_ten_memes()
    if memes is None:
        return createErrorResponse("Error fetching memes")
    return createSuccessResponse([MemeResponseData(
        id=meme.id,
        url=meme.url,
        caption=meme.caption,
        upvotes=meme.upvotes,
        image=meme.image
        ) for meme in memes])

@app.get("/api/meme/random/")
async def get_random_meme():
    meme = await pg.get_random_meme()
    if meme is None:
        return createErrorResponse("No memes found")
    return createSuccessResponse(MemeResponseData(
        id=meme.id,
        url=meme.url,
        caption=meme.caption,
        upvotes=meme.upvotes,
        image=meme.image
        )
    )