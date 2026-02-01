from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_operations_dict import ModelOperationsDict
    from ..models.model_status_dict import ModelStatusDict
    from ..models.model_version_dict import ModelVersionDict


T = TypeVar("T", bound="ModelCreate")


@_attrs_define
class ModelCreate:
    """Create new model - inherits all ModelBase fields

    Attributes:
        name (str):
        familyid (int):
        model_status (ModelStatusDict | None | Unset):
        version (ModelVersionDict | None | Unset):
        note (None | str | Unset):
        shortname (None | str | Unset):
        operations (ModelOperationsDict | None | Unset):
        description (None | str | Unset):
        date_updated (datetime.datetime | None | Unset):
    """

    name: str
    familyid: int
    model_status: ModelStatusDict | None | Unset = UNSET
    version: ModelVersionDict | None | Unset = UNSET
    note: None | str | Unset = UNSET
    shortname: None | str | Unset = UNSET
    operations: ModelOperationsDict | None | Unset = UNSET
    description: None | str | Unset = UNSET
    date_updated: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_operations_dict import ModelOperationsDict
        from ..models.model_status_dict import ModelStatusDict
        from ..models.model_version_dict import ModelVersionDict

        name = self.name

        familyid = self.familyid

        model_status: dict[str, Any] | None | Unset
        if isinstance(self.model_status, Unset):
            model_status = UNSET
        elif isinstance(self.model_status, ModelStatusDict):
            model_status = self.model_status.to_dict()
        else:
            model_status = self.model_status

        version: dict[str, Any] | None | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        elif isinstance(self.version, ModelVersionDict):
            version = self.version.to_dict()
        else:
            version = self.version

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        shortname: None | str | Unset
        if isinstance(self.shortname, Unset):
            shortname = UNSET
        else:
            shortname = self.shortname

        operations: dict[str, Any] | None | Unset
        if isinstance(self.operations, Unset):
            operations = UNSET
        elif isinstance(self.operations, ModelOperationsDict):
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
                "familyid": familyid,
            }
        )
        if model_status is not UNSET:
            field_dict["model_status"] = model_status
        if version is not UNSET:
            field_dict["version"] = version
        if note is not UNSET:
            field_dict["note"] = note
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
        from ..models.model_operations_dict import ModelOperationsDict
        from ..models.model_status_dict import ModelStatusDict
        from ..models.model_version_dict import ModelVersionDict

        d = dict(src_dict)
        name = d.pop("name")

        familyid = d.pop("familyid")

        def _parse_model_status(data: object) -> ModelStatusDict | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                model_status_type_0 = ModelStatusDict.from_dict(data)

                return model_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelStatusDict | None | Unset, data)

        model_status = _parse_model_status(d.pop("model_status", UNSET))

        def _parse_version(data: object) -> ModelVersionDict | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                version_type_0 = ModelVersionDict.from_dict(data)

                return version_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelVersionDict | None | Unset, data)

        version = _parse_version(d.pop("version", UNSET))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_shortname(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        shortname = _parse_shortname(d.pop("shortname", UNSET))

        def _parse_operations(data: object) -> ModelOperationsDict | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                operations_type_0 = ModelOperationsDict.from_dict(data)

                return operations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelOperationsDict | None | Unset, data)

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
            familyid=familyid,
            model_status=model_status,
            version=version,
            note=note,
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
