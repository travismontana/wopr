from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    game_catalog_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/images/gameid/names/{game_catalog_id}/".format(
            game_catalog_id=quote(str(game_catalog_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> HTTPValidationError | None:
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    game_catalog_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError]:
    """Get Images By Game Catalog Id Names

    Args:
        game_catalog_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError]
    """

    kwargs = _get_kwargs(
        game_catalog_id=game_catalog_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    game_catalog_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | None:
    """Get Images By Game Catalog Id Names

    Args:
        game_catalog_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError
    """

    return sync_detailed(
        game_catalog_id=game_catalog_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    game_catalog_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError]:
    """Get Images By Game Catalog Id Names

    Args:
        game_catalog_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError]
    """

    kwargs = _get_kwargs(
        game_catalog_id=game_catalog_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    game_catalog_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | None:
    """Get Images By Game Catalog Id Names

    Args:
        game_catalog_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError
    """

    return (
        await asyncio_detailed(
            game_catalog_id=game_catalog_id,
            client=client,
        )
    ).parsed
