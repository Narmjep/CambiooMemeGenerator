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
        print("-----------------")


if __name__ == "__main__":
    asyncio.run(main())