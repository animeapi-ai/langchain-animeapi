"""AnimeAPI tool for LangChain and LangGraph agents (https://animeapi.ai).

Anime image generation at $0.003 per image.

    from langchain_animeapi import AnimeAPIGenerateImage

    tool = AnimeAPIGenerateImage()  # reads ANIMEAPI_API_KEY
    print(tool.invoke({"prompt": "a silver-haired girl reading under a cherry tree"}))
"""

from ._version import __version__
from .tools import AnimeAPIGenerateImage, AnimeAPIGenerateImageInput

__all__ = ["AnimeAPIGenerateImage", "AnimeAPIGenerateImageInput", "__version__"]
