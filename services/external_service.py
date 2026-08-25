import httpx
from exceptions.external_exceptions import (
    UpstreamApiError,
    UpstreamNotFoundError,
    UpstreamTimeoutError,
)
from schemas.external import PostResponse

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT_SECONDS = 5.0


async def get_external_post(post_id: int) -> PostResponse:
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        try:
            response = await client.get(f"{BASE_URL}/posts/{post_id}")

            if response.status_code == 404:
                raise UpstreamNotFoundError()

            response.raise_for_status()
            return PostResponse.model_validate(response.json())

        except httpx.TimeoutException:
            raise UpstreamTimeoutError()
        except UpstreamNotFoundError:
            raise
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise UpstreamApiError()
