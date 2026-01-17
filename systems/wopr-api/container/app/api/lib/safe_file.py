# safe_fs.py
from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


class SafeFSError(Exception):
    """Base exception for safe fs operations."""


class PathEscapeError(SafeFSError):
    """Raised when a path tries to escape the base directory."""


class SymlinkNotAllowedError(SafeFSError):
    """Raised when a path is a symlink (or contains symlink) and policy forbids it."""


class NotFoundError(SafeFSError):
    """Raised when a required path does not exist."""


class ExistsError(SafeFSError):
    """Raised when a destination exists and policy forbids overwrite."""


@dataclass(frozen=True)
class SafeFS:
    """
    Safe file operations constrained to a base directory.

    Security model:
      - All inputs are treated as *relative paths* within base_dir.
      - Paths are resolved and verified to remain within base_dir.
      - Optional symlink policy:
          - forbid_symlinks=True blocks operating on symlinks and (optionally) paths that traverse symlinked dirs.
      - Operations avoid shell execution and prefer atomic primitives where possible.
    """
    base_dir: Path
    forbid_symlinks: bool = True
    forbid_symlink_traversal: bool = True  # stronger: rejects any symlink in parent chain
    allow_overwrite: bool = False

    def __post_init__(self):
        bd = self.base_dir.expanduser().resolve()
        object.__setattr__(self, "base_dir", bd)

    # ---------- core path handling ----------
    def _reject_absolute(self, rel: str) -> None:
        p = Path(rel)
        if p.is_absolute():
            raise PathEscapeError(f"Absolute paths are not allowed: {rel}")
        # Normalize "weird" paths early (still verify after resolve)
        if rel.strip() == "":
            raise SafeFSError("Empty path is not allowed")

    def _resolve_rel(self, rel: str, must_exist: bool = False) -> Path:
        """
        Resolve rel path against base_dir and ensure it stays inside base_dir.
        """
        self._reject_absolute(rel)

        candidate = (self.base_dir / rel)

        # Resolve without requiring existence first (so we can create new targets).
        # But for must_exist paths, resolve() will also canonicalize fully.
        try:
            resolved = candidate.resolve(strict=must_exist)
        except FileNotFoundError:
            raise NotFoundError(f"Path does not exist: {rel}")

        # Ensure resolved is within base_dir
        if resolved == self.base_dir:
            # allow base dir itself only if rel points to "."
            # treat everything else as suspicious
            pass

        if self.base_dir not in resolved.parents and resolved != self.base_dir:
            raise PathEscapeError(f"Path escapes base directory: {rel} -> {resolved}")

        if self.forbid_symlinks:
            # Reject if the final target is a symlink
            if resolved.exists() and resolved.is_symlink():
                raise SymlinkNotAllowedError(f"Symlinks not allowed: {rel}")

            if self.forbid_symlink_traversal:
                # Reject if any parent component is a symlink.
                # This prevents 'base/subdir' being a symlink to elsewhere.
                # Walk from base_dir to resolved, checking each component.
                current = self.base_dir
                for part in Path(rel).parts:
                    current = (current / part)
                    # If it exists and is a symlink, block.
                    # For non-existing path components (e.g., creating new files),
                    # we stop checking deeper.
                    if current.exists() and current.is_symlink():
                        raise SymlinkNotAllowedError(f"Symlink traversal not allowed at: {current}")
                    if not current.exists():
                        break

        return resolved

    def _ensure_parent_dir(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    # ---------- operations ----------
    def listdir(self, rel_dir: str = ".") -> list[str]:
        d = self._resolve_rel(rel_dir, must_exist=True)
        if not d.is_dir():
            raise SafeFSError(f"Not a directory: {rel_dir}")
        return sorted([p.name for p in d.iterdir()])

    def mkdir(self, rel_dir: str, exist_ok: bool = True) -> None:
        d = self._resolve_rel(rel_dir, must_exist=False)
        d.mkdir(parents=True, exist_ok=exist_ok)

    def remove_file(self, rel_path: str) -> None:
        p = self._resolve_rel(rel_path, must_exist=True)
        if p.is_dir():
            raise SafeFSError(f"Expected file, got directory: {rel_path}")
        p.unlink()

    def rmtree(self, rel_dir: str) -> None:
        d = self._resolve_rel(rel_dir, must_exist=True)
        if not d.is_dir():
            raise SafeFSError(f"Expected directory: {rel_dir}")
        # shutil.rmtree has symlink-related footguns; our checks reduce risk.
        shutil.rmtree(d)

    def move(self, rel_src: str, rel_dst: str) -> None:
        src = self._resolve_rel(rel_src, must_exist=True)
        dst = self._resolve_rel(rel_dst, must_exist=False)

        if dst.exists() and not self.allow_overwrite:
            raise ExistsError(f"Destination exists: {rel_dst}")

        self._ensure_parent_dir(dst)

        # Prefer atomic rename on same filesystem.
        try:
            os.replace(src, dst)  # atomic if same fs; overwrites if exists
            if not self.allow_overwrite and dst.exists() and src.exists():
                # Defensive (shouldn't happen)
                raise SafeFSError("Unexpected state after replace()")
            return "os"
        except OSError:
            # Cross-device move or other errors: fall back to shutil.move
            # Note: shutil.move may copy+delete; still constrained by our path jail.
            shutil.move(str(src), str(dst))
            return "shutil"

    def copy_file(self, rel_src: str, rel_dst: str) -> None:
        src = self._resolve_rel(rel_src, must_exist=True)
        if src.is_dir():
            raise SafeFSError(f"copy_file expects a file, got directory: {rel_src}")

        dst = self._resolve_rel(rel_dst, must_exist=False)
        if dst.exists() and not self.allow_overwrite:
            raise ExistsError(f"Destination exists: {rel_dst}")

        self._ensure_parent_dir(dst)

        # Copy to temp in same dir then replace for atomic-ish behavior.
        with tempfile.NamedTemporaryFile(dir=str(dst.parent), delete=False) as tf:
            tmp = Path(tf.name)
        try:
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except Exception:
                    pass

    def copytree(self, rel_src_dir: str, rel_dst_dir: str) -> None:
        src = self._resolve_rel(rel_src_dir, must_exist=True)
        if not src.is_dir():
            raise SafeFSError(f"Expected directory: {rel_src_dir}")

        dst = self._resolve_rel(rel_dst_dir, must_exist=False)
        if dst.exists() and not self.allow_overwrite:
            raise ExistsError(f"Destination exists: {rel_dst_dir}")

        self._ensure_parent_dir(dst)

        # dirs_exist_ok is py3.8+; we keep it strict unless overwrite is allowed
        shutil.copytree(src, dst, dirs_exist_ok=self.allow_overwrite)

    def atomic_write_text(self, rel_path: str, data: str, encoding: str = "utf-8") -> None:
        dst = self._resolve_rel(rel_path, must_exist=False)
        if dst.exists() and dst.is_dir():
            raise SafeFSError(f"Expected file path, got directory: {rel_path}")

        self._ensure_parent_dir(dst)

        with tempfile.NamedTemporaryFile(dir=str(dst.parent), delete=False) as tf:
            tmp = Path(tf.name)
            tf.write(data.encode(encoding))

        try:
            if dst.exists() and not self.allow_overwrite:
                raise ExistsError(f"Destination exists: {rel_path}")
            os.replace(tmp, dst)
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except Exception:
                    pass
