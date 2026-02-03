from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_project_api_v2_vision_projects_project_id_get_response_get_project_api_v2_vision_projects_project_id_get import (
    GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    project_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/vision/projects/{project_id}".format(
            project_id=quote(str(project_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = (
            GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet.from_dict(
                response.json()
            )
        )

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
) -> Response[
    GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet | HTTPValidationError
]:
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
) -> Response[
    GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet | HTTPValidationError
]:
    """Get Project

     Get specific Label Studio project details.

    Args:
        project_id: Label Studio project ID

    Returns:
        Project details

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet | HTTPValidationError]
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
) -> (
    GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet
    | HTTPValidationError
    | None
):
    """Get Project

     Get specific Label Studio project details.

    Args:
        project_id: Label Studio project ID

    Returns:
        Project details

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet | HTTPValidationError
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet | HTTPValidationError
]:
    """Get Project

     Get specific Label Studio project details.

    Args:
        project_id: Label Studio project ID

    Returns:
        Project details

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet | HTTPValidationError]
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
) -> (
    GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet
    | HTTPValidationError
    | None
):
    """Get Project

     Get specific Label Studio project details.

    Args:
        project_id: Label Studio project ID

    Returns:
        Project details

    Args:
        project_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetProjectApiV2VisionProjectsProjectIdGetResponseGetProjectApiV2VisionProjectsProjectIdGet | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
        )
    ).parsed
