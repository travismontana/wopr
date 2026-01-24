from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.task_create_response_data import TaskCreateResponseData


T = TypeVar("T", bound="TaskCreateResponse")


@_attrs_define
class TaskCreateResponse:
    """Task creation response

    Attributes:
        id (int):
        project (int):
        data (TaskCreateResponseData):
    """

    id: int
    project: int
    data: TaskCreateResponseData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        project = self.project

        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "project": project,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_create_response_data import TaskCreateResponseData

        d = dict(src_dict)
        id = d.pop("id")

        project = d.pop("project")

        data = TaskCreateResponseData.from_dict(d.pop("data"))

        task_create_response = cls(
            id=id,
            project=project,
            data=data,
        )

        task_create_response.additional_properties = d
        return task_create_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
