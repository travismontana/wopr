from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_tasks_api_v2_vision_projects_project_id_tasks_get_response_200_item import (
    ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item,
)
from ...types import Response


def _get_kwargs(
    project_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/vision/projects/{project_id}/tasks".format(
            project_id=quote(str(project_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item.from_dict(
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
) -> Response[HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item]]:
    """List Tasks

     List all annotation tasks (images) in a Label Studio project.

    Args:
        project_id: Label Studio project ID

    Returns:
        Tasks list with image data

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item] | None:
    """List Tasks

     List all annotation tasks (images) in a Label Studio project.

    Args:
        project_id: Label Studio project ID

    Returns:
        Tasks list with image data

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item]
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item]]:
    """List Tasks

     List all annotation tasks (images) in a Label Studio project.

    Args:
        project_id: Label Studio project ID

    Returns:
        Tasks list with image data

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item]]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item] | None:
    """List Tasks

     List all annotation tasks (images) in a Label Studio project.

    Args:
        project_id: Label Studio project ID

    Returns:
        Tasks list with image data

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ListTasksApiV2VisionProjectsProjectIdTasksGetResponse200Item]
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
        )
    ).parsed
