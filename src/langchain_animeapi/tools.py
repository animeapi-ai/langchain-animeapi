from __future__ import annotations

from typing import Any, Dict, Literal, Optional, Tuple, Type

from animeapi import AnimeAPI, AnimeAPIError, AsyncAnimeAPI
from langchain_core.callbacks import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field, SecretStr

PRICES_USD = {"anime": 0.003, "ultra": 0.01, "ultra-max": 0.02}


class AnimeAPIGenerateImageInput(BaseModel):
    """What the model fills in when it calls the tool."""

    prompt: str = Field(
        description=(
            "What to draw: subject, appearance, pose, setting, lighting. "
            "Plain English works best. At most 1000 characters."
        ),
        max_length=1000,
    )
    orientation: Literal["portrait", "square", "landscape"] = Field(
        default="portrait",
        description=(
            "Shape of the image: portrait (characters, full body), square (avatars, icons) "
            "or landscape (scenery, wide scenes). Same price for every shape."
        ),
    )


class AnimeAPIGenerateImage(BaseTool):
    """Generate an anime image with AnimeAPI: $0.003 per image on the default model.

    Setup:
        ``pip install langchain-animeapi`` and set ``ANIMEAPI_API_KEY`` (keys start with
        ``ank_``; create one at https://animeapi.ai/dashboard/api-keys).

    The model chooses the prompt and the shape. You choose the image model here, so an
    agent cannot switch to a more expensive one:

        tool = AnimeAPIGenerateImage(model="anime")   # $0.003 per image (default)
        tool = AnimeAPIGenerateImage(model="ultra")   # $0.01 per image

    The tool returns a short text for the model (the image URL, price and balance left)
    and, as the artifact, a dict with ``image_url``, ``enhanced_prompt``, ``model``,
    ``orientation``, ``price_usd``, ``balance_usd`` and ``generation_time_ms``.
    """

    name: str = "animeapi_generate_image"
    description: str = (
        "Generate one anime-style image from a text description and return its URL. "
        "Costs $0.003 per image on the default model. Describe the subject, appearance, pose, "
        "setting and lighting in plain English. Adult content is not available; explicit prompts are refused and not charged."
    )
    args_schema: Type[BaseModel] = AnimeAPIGenerateImageInput
    response_format: Literal["content", "content_and_artifact"] = "content_and_artifact"
    handle_tool_error: bool = True

    api_key: Optional[SecretStr] = Field(default=None, description="Defaults to ANIMEAPI_API_KEY.")
    model: Literal["anime", "ultra", "ultra-max"] = "anime"
    enhance: bool = True
    timeout: float = 120.0
    max_retries: int = 2

    def _client_kwargs(self) -> Dict[str, Any]:
        return {
            "api_key": self.api_key.get_secret_value() if self.api_key else None,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }

    def _result(self, image: Any, orientation: str) -> Tuple[str, Dict[str, Any]]:
        price = PRICES_USD[self.model]
        content = (
            f"Image generated: {image.image_url}\n"
            f"Model {self.model}, {orientation}, ${price}. Balance left: ${image.balance_usd}.\n"
            "The link is not permanent storage; download the image to keep it."
        )
        artifact = {
            "image_url": image.image_url,
            "enhanced_prompt": image.enhanced_prompt,
            "model": self.model,
            "orientation": orientation,
            "price_usd": price,
            "balance_usd": image.balance_usd,
            "generation_time_ms": image.generation_time_ms,
        }
        return content, artifact

    @staticmethod
    def _tool_error(e: AnimeAPIError) -> ToolException:
        # The API's own message, e.g. why a prompt was refused or that the balance is empty.
        return ToolException(f"AnimeAPI: {e.message} ({e.code or e.status})")

    def _run(
        self,
        prompt: str,
        orientation: str = "portrait",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        try:
            with AnimeAPI(**self._client_kwargs()) as client:
                image = client.images.generate(
                    prompt, model=self.model, orientation=orientation, enhance=self.enhance  # type: ignore[arg-type]
                )
        except AnimeAPIError as e:
            raise self._tool_error(e) from e
        return self._result(image, orientation)

    async def _arun(
        self,
        prompt: str,
        orientation: str = "portrait",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        try:
            async with AsyncAnimeAPI(**self._client_kwargs()) as client:
                image = await client.images.generate(
                    prompt, model=self.model, orientation=orientation, enhance=self.enhance  # type: ignore[arg-type]
                )
        except AnimeAPIError as e:
            raise self._tool_error(e) from e
        return self._result(image, orientation)
