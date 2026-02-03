from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelUpdate")


@_attrs_define
class ModelUpdate:
    """Update existing model - all fields optional

    Attributes:
        name (None | str | Unset):
        description (None | str | Unset):
        note (None | str | Unset):
        version (int | None | Unset):
        model_status (None | str | Unset):
        familyid (int | None | Unset):
        shortname (None | str | Unset):
        date_updated (datetime.datetime | None | Unset):
        url (None | str | Unset):
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    note: None | str | Unset = UNSET
    version: int | None | Unset = UNSET
    model_status: None | str | Unset = UNSET
    familyid: int | None | Unset = UNSET
    shortname: None | str | Unset = UNSET
    date_updated: datetime.datetime | None | Unset = UNSET
    url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        version: int | None | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        model_status: None | str | Unset
        if isinstance(self.model_status, Unset):
            model_status = UNSET
        else:
            model_status = self.model_status

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

        date_updated: None | str | Unset
        if isinstance(self.date_updated, Unset):
            date_updated = UNSET
        elif isinstance(self.date_updated, datetime.datetime):
            date_updated = self.date_updated.isoformat()
        else:
            date_updated = self.date_updated

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if note is not UNSET:
            field_dict["note"] = note
        if version is not UNSET:
            field_dict["version"] = version
        if model_status is not UNSET:
            field_dict["model_status"] = model_status
        if familyid is not UNSET:
            field_dict["familyid"] = familyid
        if shortname is not UNSET:
            field_dict["shortname"] = shortname
        if date_updated is not UNSET:
            field_dict["date_updated"] = date_updated
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_version(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        version = _parse_version(d.pop("version", UNSET))

        def _parse_model_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model_status = _parse_model_status(d.pop("model_status", UNSET))

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

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        model_update = cls(
            name=name,
            description=description,
            note=note,
            version=version,
            model_status=model_status,
            familyid=familyid,
            shortname=shortname,
            date_updated=date_updated,
            url=url,
        )

        model_update.additional_properties = d
        return model_update

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
