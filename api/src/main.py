"""
Contains the main FastAPI application code and routes
"""

import pg as pg
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import io
import easyocr


import json
import requests
import base64
from enum import Enum

app = FastAPI()

reader = easyocr.Reader(["de"])


class VoteType(str, Enum):
    upvote = "upvote"
    downvote = "downvote"

class VoteData(BaseModel):
    """Data passed in json format to upvote or downvote a meme
    """

    # The type of vote: either "upvote" or "downvote"
    type: VoteType


class MemeCreationData(BaseModel):
    """Data passed in json format to create a meme
    """

    url: Optional[str] = ""
    image: Optional[str] = ""
    caption: Optional[str] = ""

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

def createSuccessResponse(data=None):
    if data is None:
        return {"status": "success"}
    return {"status": "success", "data": data}

def createErrorResponse(error):
    print("Error:", error)
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
    
def get_text_from_image(image: bytes) -> str:
    """Extracts text from an image using easyocr

    Args:
        image (bytes): The image to extract text from

    Returns:
        str: The extracted text
    """

    extracted = reader.readtext(image, detail=0)
    return " ".join(extracted)
        
    
    
    


@app.post("/api/meme/")
async def create_meme(meme: MemeCreationData) -> dict:
    """Creates a new meme and stores it in the database.

    Args:
        meme (MemeCreationData): Data must be passed in JSON format in the request body.

    Returns:
        dict: A success response or an error response.
    """
    
    # Ensure that either the url or the image is provided
    url_set = meme.url != ""
    image_set = meme.image != ""

    image_bytes : bytes

    print("-" * 50)

    if not url_set and not image_set:
        return createErrorResponse("Either the url or image must be provided")
    
    # Prefer URL over image
    if url_set and image_set:
        image_set = False
    
    if url_set:
        content = get_url_content(meme.url) # type: ignore
        if content is None:
            return createErrorResponse("Failed to fetch URL content for " + meme.url) # type: ignore
        
        meme.image = base64.b64encode(content).decode("utf-8")
        image_bytes = content
    else:
        try:
            image_bytes = base64.b64decode(meme.image) # type: ignore
        except Exception as e:
            return createErrorResponse("Invalid base64 image")

    # Use easyocr to extract text from the image
    if meme.caption == "":
        text = get_text_from_image(image_bytes)
        if text == "":
            return createErrorResponse("Failed to extract text from image. Make sure the provided image is not too large. Please choose another image or provide a caption.")
        
        meme.caption = text
        
    await pg.create_meme(meme.url, meme.caption, meme.image) # type: ignore
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