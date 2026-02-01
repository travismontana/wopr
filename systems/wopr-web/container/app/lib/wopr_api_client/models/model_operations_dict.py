from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ModelOperationsDict")


@_attrs_define
class ModelOperationsDict:
    """Model operation tracking

    Attributes:
        task (str):
        data (str):
        note (str):
        extradata (str):
        status (str):
    """

    task: str
    data: str
    note: str
    extradata: str
    status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        task = self.task

        data = self.data

        note = self.note

        extradata = self.extradata

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "task": task,
                "data": data,
                "note": note,
                "extradata": extradata,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        task = d.pop("task")

        data = d.pop("data")

        note = d.pop("note")

        extradata = d.pop("extradata")

        status = d.pop("status")

        model_operations_dict = cls(
            task=task,
            data=data,
            note=note,
            extradata=extradata,
            status=status,
        )

        model_operations_dict.additional_properties = d
        return model_operations_dict

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
