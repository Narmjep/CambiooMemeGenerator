import pg as pg
from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

class MemeCreationData(BaseModel):
    url: str
    caption: str

class MemeResponseData(BaseModel):
    id: int
    url: str
    caption: str
    upvotes: int

def createSuccessResponse(data=None):
    if data is None:
        return {"status": "success"}
    return {"status": "success", "data": data}

def createErrorResponse(error):
    return {"status": "error", "error": error}


@app.post("/api/meme/")
async def create_meme(meme: MemeCreationData):
    print(meme)
    await pg.create_meme(meme.url, meme.caption)
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
        upvotes=meme.upvotes
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
        upvotes=meme.upvotes
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
        upvotes=meme.upvotes
        )
    )