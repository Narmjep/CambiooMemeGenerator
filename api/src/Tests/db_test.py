from ..pg import *
import pytest

"""
@pytest.mark.asyncio
async def test_create_meme():
    await destroy_db()
    await init_db()
    await create_meme("https://www.google.com", "This is a test meme")
    memes = await get_all_memes()
    assert len(memes) == 1
    assert memes[0].url == "https://www.google.com"
    assert memes[0].caption == "This is a test meme"

"""