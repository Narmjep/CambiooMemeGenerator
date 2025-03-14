"""
A tool that displays all memes in the database
"""

from src.pg import *
import asyncio


async def main():
    memes = await get_all_memes()
    for meme in memes:
        print("-----------------")
        print("ID:", meme.id)
        print("URL:", meme.url)
        print("Caption:", meme.caption)
        print("Upvotes:", meme.upvotes)
        print("Image: " + meme.image[:50] + "...")
        print("-----------------")


if __name__ == "__main__":
    asyncio.run(main())