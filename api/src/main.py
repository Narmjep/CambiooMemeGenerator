"""
Contains the main FastAPI application code and routes
"""

import pg as pg
from fastapi import FastAPI
from pydantic import BaseModel
import json
import requests
import base64
from enum import Enum

app = FastAPI()

class MemeCreationData(BaseModel):
    """Data passed in json format to create a meme
    """

    url: str
    caption: str

class MemeResponseData(BaseModel):
    """Data returned in json format by the api
    """

    # A unique identifier for the meme
    id: int
    # The url of the assigned image
    url: str
    # The caption of the meme
    caption: str
    # The number of upvotes the meme has
    upvotes: int
    # The base64 encoded image
    image: str

class VoteType(str, Enum):
    upvote = "upvote"
    downvote = "downvote"

class VoteData(BaseModel):
    """Data passed in json format to upvote or downvote a meme
    """

    # The type of vote: either "upvote" or "downvote"
    type: VoteType




def createSuccessResponse(data=None):
    if data is None:
        return {"status": "success"}
    return {"status": "success", "data": data}

def createErrorResponse(error):
    return {"status": "error", "error": error}


def get_url_content(url: str) -> bytes | None:
    """Fetches the content of a url

    Args:
        url (str): The url to fetch

    Returns:
        bytes | None: if the url is valid, the content of the url is returned. Otherwise, None is returned
    """

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.content
    except requests.exceptions.RequestException as e:
        return None

@app.post("/api/meme/")
async def create_meme(meme: MemeCreationData) -> dict:
    """Creates a new meme and stores it in the database

    Args:
        meme (MemeCreationData): The data must be passed in the request body in json format. If the provided data is invalid, an error response is returned. Additionally, if the url is invalid, an error response is returned

    Returns:
        dict: A success response or an error response
    """

    content = get_url_content(meme.url)
    if content is None:
        return createErrorResponse("Failed to fetch url content")
    
    encoded_img = base64.b64encode(content).decode("utf-8")

    await pg.create_meme(meme.url, meme.caption, encoded_img)
    return createSuccessResponse()

@app.get("/api/meme/{id}")
async def get_meme_by_id(id: int) -> dict:
    """Retrieves a meme by its id

    Args:
        id (int): The unique identifier of the meme

    Returns:
        dict: A success response containing the meme data or an error response
    """

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

@app.post("/api/meme/{id}/vote/")
async def vote_meme(id: int, vote: VoteData) -> dict:

    if vote.type == VoteType.upvote:
        res = await pg.upvote_meme(id)
    elif vote.type == VoteType.downvote:
        res = await pg.downvote_meme(id)
    else:
        return createErrorResponse("Invalid vote type")

    if not res:
        return createErrorResponse("Meme not found")
    return createSuccessResponse()

@app.get("/api/meme/top/")
async def get_top_memes():
    """Retrieves the top 10 memes by upvotes

    Returns:
        dict: A success response containing the top 10 memes (or less) or an error response if there was an issue fetching the memes
    """

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
    """Returns a random meme

    Returns:
        dict: A success response containing a random meme or an error response if there was an issue fetching the meme
    """

    meme = await pg.get_random_meme()
    if meme is None:
        return createErrorResponse("Error fetching meme")
    return createSuccessResponse(MemeResponseData(
        id=meme.id,
        url=meme.url,
        caption=meme.caption,
        upvotes=meme.upvotes,
        image=meme.image
        )
    )