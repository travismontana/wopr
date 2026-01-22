from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    environment: str | Unset = "production",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["environment"] = environment

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/config/all",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    environment: str | Unset = "production",
) -> Response[Any | HTTPValidationError]:
    """Get All

     Get entire configuration for specified environment.
    Proxies request to Directus API.

    Args:
        environment: Config environment (production, stage, dev)

    Returns:
        Configuration JSONB document

    Args:
        environment (str | Unset):  Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        environment=environment,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    environment: str | Unset = "production",
) -> Any | HTTPValidationError | None:
    """Get All

     Get entire configuration for specified environment.
    Proxies request to Directus API.

    Args:
        environment: Config environment (production, stage, dev)

    Returns:
        Configuration JSONB document

    Args:
        environment (str | Unset):  Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        environment=environment,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    environment: str | Unset = "production",
) -> Response[Any | HTTPValidationError]:
    """Get All

     Get entire configuration for specified environment.
    Proxies request to Directus API.

    Args:
        environment: Config environment (production, stage, dev)

    Returns:
        Configuration JSONB document

    Args:
        environment (str | Unset):  Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        environment=environment,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    environment: str | Unset = "production",
) -> Any | HTTPValidationError | None:
    """Get All

     Get entire configuration for specified environment.
    Proxies request to Directus API.

    Args:
        environment: Config environment (production, stage, dev)

    Returns:
        Configuration JSONB document

    Args:
        environment (str | Unset):  Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            environment=environment,
        )
    ).parsed
