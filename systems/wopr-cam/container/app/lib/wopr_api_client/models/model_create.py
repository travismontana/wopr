from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_create_model_status import ModelCreateModelStatus
    from ..models.model_create_operations_type_0 import ModelCreateOperationsType0
    from ..models.model_create_version import ModelCreateVersion


T = TypeVar("T", bound="ModelCreate")


@_attrs_define
class ModelCreate:
    """Create new model - inherits all ModelBase fields

    Attributes:
        name (str):
        model_status (ModelCreateModelStatus):
        version (ModelCreateVersion):
        note (None | str | Unset):
        familyid (int | None | Unset):
        shortname (None | str | Unset):
        operations (ModelCreateOperationsType0 | None | Unset):
        description (None | str | Unset):
        date_updated (datetime.datetime | None | Unset):
    """

    name: str
    model_status: ModelCreateModelStatus
    version: ModelCreateVersion
    note: None | str | Unset = UNSET
    familyid: int | None | Unset = UNSET
    shortname: None | str | Unset = UNSET
    operations: ModelCreateOperationsType0 | None | Unset = UNSET
    description: None | str | Unset = UNSET
    date_updated: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_create_operations_type_0 import ModelCreateOperationsType0

        name = self.name

        model_status = self.model_status.to_dict()

        version = self.version.to_dict()

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        familyid: int | None | Unset
        if isinstance(self.familyid, Unset):
            familyid = UNSET
        else:
            familyid = self.familyid

        shortname: None | str | Unset
        if isinstance(self.shortname, Unset):
            shortname = UNSET
        else:
            shortname = self.shortname

        operations: dict[str, Any] | None | Unset
        if isinstance(self.operations, Unset):
            operations = UNSET
        elif isinstance(self.operations, ModelCreateOperationsType0):
            operations = self.operations.to_dict()
        else:
            operations = self.operations

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        date_updated: None | str | Unset
        if isinstance(self.date_updated, Unset):
            date_updated = UNSET
        elif isinstance(self.date_updated, datetime.datetime):
            date_updated = self.date_updated.isoformat()
        else:
            date_updated = self.date_updated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "model_status": model_status,
                "version": version,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if familyid is not UNSET:
            field_dict["familyid"] = familyid
        if shortname is not UNSET:
            field_dict["shortname"] = shortname
        if operations is not UNSET:
            field_dict["operations"] = operations
        if description is not UNSET:
            field_dict["description"] = description
        if date_updated is not UNSET:
            field_dict["date_updated"] = date_updated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_create_model_status import ModelCreateModelStatus
        from ..models.model_create_operations_type_0 import ModelCreateOperationsType0
        from ..models.model_create_version import ModelCreateVersion

        d = dict(src_dict)
        name = d.pop("name")

        model_status = ModelCreateModelStatus.from_dict(d.pop("model_status"))

        version = ModelCreateVersion.from_dict(d.pop("version"))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_familyid(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        familyid = _parse_familyid(d.pop("familyid", UNSET))

        def _parse_shortname(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        shortname = _parse_shortname(d.pop("shortname", UNSET))

        def _parse_operations(data: object) -> ModelCreateOperationsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                operations_type_0 = ModelCreateOperationsType0.from_dict(data)

                return operations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelCreateOperationsType0 | None | Unset, data)

        operations = _parse_operations(d.pop("operations", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_date_updated(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                date_updated_type_0 = isoparse(data)

                return date_updated_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        date_updated = _parse_date_updated(d.pop("date_updated", UNSET))

        model_create = cls(
            name=name,
            model_status=model_status,
            version=version,
            note=note,
            familyid=familyid,
            shortname=shortname,
            operations=operations,
            description=description,
            date_updated=date_updated,
        )

        model_create.additional_properties = d
        return model_create

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
