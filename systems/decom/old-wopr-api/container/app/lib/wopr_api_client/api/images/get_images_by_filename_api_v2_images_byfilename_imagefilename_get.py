from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_images_by_filename_api_v2_images_byfilename_imagefilename_get_response_200_item import (
    GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    imagefilename: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/images/byfilename/{imagefilename}".format(
            imagefilename=quote(str(imagefilename), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    imagefilename: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item]]:
    """Get Images By Filename

    Args:
        imagefilename (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item]]
    """

    kwargs = _get_kwargs(
        imagefilename=imagefilename,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    imagefilename: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item] | None:
    """Get Images By Filename

    Args:
        imagefilename (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item]
    """

    return sync_detailed(
        imagefilename=imagefilename,
        client=client,
    ).parsed


async def asyncio_detailed(
    imagefilename: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item]]:
    """Get Images By Filename

    Args:
        imagefilename (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item]]
    """

    kwargs = _get_kwargs(
        imagefilename=imagefilename,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    imagefilename: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item] | None:
    """Get Images By Filename

    Args:
        imagefilename (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[GetImagesByFilenameApiV2ImagesByfilenameImagefilenameGetResponse200Item]
    """

    return (
        await asyncio_detailed(
            imagefilename=imagefilename,
            client=client,
        )
    ).parsed
