from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_status_dict_backup_type_0 import ModelStatusDictBackupType0


T = TypeVar("T", bound="ModelStatusDict")


@_attrs_define
class ModelStatusDict:
    """Runtime file status for wopr-model service

    Attributes:
        active (bool):
        backup (ModelStatusDictBackupType0 | None | Unset):
        checksum (None | str | Unset):
        has_distfile (bool | None | Unset):
        filename (None | str | Unset):
    """

    active: bool
    backup: ModelStatusDictBackupType0 | None | Unset = UNSET
    checksum: None | str | Unset = UNSET
    has_distfile: bool | None | Unset = UNSET
    filename: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_status_dict_backup_type_0 import ModelStatusDictBackupType0

        active = self.active

        backup: dict[str, Any] | None | Unset
        if isinstance(self.backup, Unset):
            backup = UNSET
        elif isinstance(self.backup, ModelStatusDictBackupType0):
            backup = self.backup.to_dict()
        else:
            backup = self.backup

        checksum: None | str | Unset
        if isinstance(self.checksum, Unset):
            checksum = UNSET
        else:
            checksum = self.checksum

        has_distfile: bool | None | Unset
        if isinstance(self.has_distfile, Unset):
            has_distfile = UNSET
        else:
            has_distfile = self.has_distfile

        filename: None | str | Unset
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "active": active,
            }
        )
        if backup is not UNSET:
            field_dict["backup"] = backup
        if checksum is not UNSET:
            field_dict["checksum"] = checksum
        if has_distfile is not UNSET:
            field_dict["has_distfile"] = has_distfile
        if filename is not UNSET:
            field_dict["filename"] = filename

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_status_dict_backup_type_0 import ModelStatusDictBackupType0

        d = dict(src_dict)
        active = d.pop("active")

        def _parse_backup(data: object) -> ModelStatusDictBackupType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backup_type_0 = ModelStatusDictBackupType0.from_dict(data)

                return backup_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelStatusDictBackupType0 | None | Unset, data)

        backup = _parse_backup(d.pop("backup", UNSET))

        def _parse_checksum(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        checksum = _parse_checksum(d.pop("checksum", UNSET))

        def _parse_has_distfile(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        has_distfile = _parse_has_distfile(d.pop("has_distfile", UNSET))

        def _parse_filename(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename = _parse_filename(d.pop("filename", UNSET))

        model_status_dict = cls(
            active=active,
            backup=backup,
            checksum=checksum,
            has_distfile=has_distfile,
            filename=filename,
        )

        model_status_dict.additional_properties = d
        return model_status_dict

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
