from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_version_dict_previous_versions_type_0 import ModelVersionDictPreviousVersionsType0


T = TypeVar("T", bound="ModelVersionDict")


@_attrs_define
class ModelVersionDict:
    """Version tracking for models

    Attributes:
        current_version (int):
        note (None | str | Unset):
        wopr_version (None | str | Unset):
        previous_versions (ModelVersionDictPreviousVersionsType0 | None | Unset):
    """

    current_version: int
    note: None | str | Unset = UNSET
    wopr_version: None | str | Unset = UNSET
    previous_versions: ModelVersionDictPreviousVersionsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_version_dict_previous_versions_type_0 import ModelVersionDictPreviousVersionsType0

        current_version = self.current_version

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        wopr_version: None | str | Unset
        if isinstance(self.wopr_version, Unset):
            wopr_version = UNSET
        else:
            wopr_version = self.wopr_version

        previous_versions: dict[str, Any] | None | Unset
        if isinstance(self.previous_versions, Unset):
            previous_versions = UNSET
        elif isinstance(self.previous_versions, ModelVersionDictPreviousVersionsType0):
            previous_versions = self.previous_versions.to_dict()
        else:
            previous_versions = self.previous_versions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "current_version": current_version,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if wopr_version is not UNSET:
            field_dict["wopr_version"] = wopr_version
        if previous_versions is not UNSET:
            field_dict["previous_versions"] = previous_versions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_version_dict_previous_versions_type_0 import ModelVersionDictPreviousVersionsType0

        d = dict(src_dict)
        current_version = d.pop("current_version")

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_wopr_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        wopr_version = _parse_wopr_version(d.pop("wopr_version", UNSET))

        def _parse_previous_versions(data: object) -> ModelVersionDictPreviousVersionsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                previous_versions_type_0 = ModelVersionDictPreviousVersionsType0.from_dict(data)

                return previous_versions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelVersionDictPreviousVersionsType0 | None | Unset, data)

        previous_versions = _parse_previous_versions(d.pop("previous_versions", UNSET))

        model_version_dict = cls(
            current_version=current_version,
            note=note,
            wopr_version=wopr_version,
            previous_versions=previous_versions,
        )

        model_version_dict.additional_properties = d
        return model_version_dict

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
