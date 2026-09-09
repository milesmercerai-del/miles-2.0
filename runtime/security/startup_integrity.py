from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat
from typing import Any


class IntegrityError(RuntimeError):
    """Base class for startup-integrity failures."""


class IntegrityManifestError(IntegrityError):
    """Raised when the integrity manifest is malformed or unsafe."""


class IntegrityViolation(IntegrityError):
    """Raised when one or more protected artifacts fail verification."""


@dataclass(frozen=True)
class IntegrityTarget:
    name: str
    relative_path: str
    sha256: str
    expected_owner_uid: int | None = None


@dataclass(frozen=True)
class IntegrityResult:
    name: str
    path: str
    expected_sha256: str
    actual_sha256: str | None
    ok: bool
    reason: str


@dataclass(frozen=True)
class IntegrityReport:
    manifest_version: int
    results: tuple[IntegrityResult, ...]

    @property
    def ok(self) -> bool:
        return all(item.ok for item in self.results)

    @property
    def failures(self) -> tuple[IntegrityResult, ...]:
        return tuple(item for item in self.results if not item.ok)


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value)


def _load_manifest(
    path: Path,
    *,
    expected_owner_uid: int | None = None,
) -> tuple[int, tuple[IntegrityTarget, ...]]:
    if path.is_symlink():
        raise IntegrityManifestError("integrity_manifest_must_not_be_symlink")
    try:
        st = path.stat()
    except FileNotFoundError as exc:
        raise IntegrityManifestError("integrity_manifest_missing") from exc
    if not stat.S_ISREG(st.st_mode):
        raise IntegrityManifestError("integrity_manifest_must_be_regular_file")
    if os.name == "posix":
        if stat.S_IMODE(st.st_mode) & 0o022:
            raise IntegrityManifestError("integrity_manifest_writable_by_non_owner")
        if expected_owner_uid is not None and st.st_uid != expected_owner_uid:
            raise IntegrityManifestError("integrity_manifest_owner_mismatch")

    try:
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityManifestError("integrity_manifest_unreadable") from exc

    version = raw.get("manifest_version")
    if version != 1:
        raise IntegrityManifestError("unsupported_integrity_manifest_version")

    items = raw.get("artifacts")
    if not isinstance(items, list) or not items:
        raise IntegrityManifestError("integrity_manifest_requires_artifacts")

    names: set[str] = set()
    paths: set[str] = set()
    targets: list[IntegrityTarget] = []

    for item in items:
        if not isinstance(item, dict):
            raise IntegrityManifestError("integrity_manifest_artifact_must_be_object")

        name = item.get("name")
        relative_path = item.get("path")
        expected = item.get("sha256")
        owner_uid = item.get("owner_uid")

        if not isinstance(name, str) or not name.strip():
            raise IntegrityManifestError("integrity_manifest_invalid_name")
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise IntegrityManifestError("integrity_manifest_invalid_path")
        if not isinstance(expected, str) or not _valid_sha256(expected):
            raise IntegrityManifestError("integrity_manifest_invalid_sha256")
        if owner_uid is not None and (
            not isinstance(owner_uid, int) or isinstance(owner_uid, bool) or owner_uid < 0
        ):
            raise IntegrityManifestError("integrity_manifest_invalid_owner_uid")

        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise IntegrityManifestError("integrity_manifest_path_escape")

        normalized = candidate.as_posix()
        if name in names:
            raise IntegrityManifestError("integrity_manifest_duplicate_name")
        if normalized in paths:
            raise IntegrityManifestError("integrity_manifest_duplicate_path")

        names.add(name)
        paths.add(normalized)
        targets.append(
            IntegrityTarget(
                name=name,
                relative_path=normalized,
                sha256=expected.lower(),
                expected_owner_uid=owner_uid,
            )
        )

    return version, tuple(targets)


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Hash a regular file without following a final-component symlink."""
    target = Path(path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(target, flags)
    except OSError as exc:
        raise IntegrityViolation(f"unable_to_open_integrity_target:{target}") from exc

    try:
        mode = os.fstat(fd).st_mode
        if not stat.S_ISREG(mode):
            raise IntegrityViolation(f"integrity_target_not_regular_file:{target}")

        digest = hashlib.sha256()
        while True:
            block = os.read(fd, chunk_size)
            if not block:
                break
            digest.update(block)
        return digest.hexdigest()
    finally:
        os.close(fd)


def verify_manifest(
    manifest_path: str | Path,
    *,
    root: str | Path,
    expected_manifest_owner_uid: int | None = None,
) -> IntegrityReport:
    """Verify all artifacts listed in a protected external manifest.

    This is intended to be called by a trusted launcher before the permission
    daemon loads policy. The manifest itself must live outside Miles runtime and
    daemon ordinary write paths; a self-check from a replaceable daemon is not
    sufficient protection.
    """
    manifest = Path(manifest_path)
    root_path = Path(root).resolve()
    version, targets = _load_manifest(
        manifest,
        expected_owner_uid=expected_manifest_owner_uid,
    )

    results: list[IntegrityResult] = []
    for target in targets:
        requested = root_path / target.relative_path
        try:
            if requested.is_symlink():
                raise IntegrityViolation("integrity_target_symlink")
            resolved = requested.resolve(strict=True)
            try:
                resolved.relative_to(root_path)
            except ValueError as exc:
                raise IntegrityViolation("integrity_target_escaped_root") from exc
            if resolved != requested.absolute():
                # A parent-component symlink changed the effective path. Even
                # when it still resolves under root, reject the ambiguity.
                raise IntegrityViolation("integrity_target_path_not_canonical")

            st = resolved.stat()
            if os.name == "posix":
                if stat.S_IMODE(st.st_mode) & 0o022:
                    raise IntegrityViolation("integrity_target_writable_by_non_owner")
                if (
                    target.expected_owner_uid is not None
                    and st.st_uid != target.expected_owner_uid
                ):
                    raise IntegrityViolation("integrity_target_owner_mismatch")

            actual = sha256_file(resolved)
            ok = hmac.compare_digest(actual, target.sha256)
            results.append(
                IntegrityResult(
                    name=target.name,
                    path=target.relative_path,
                    expected_sha256=target.sha256,
                    actual_sha256=actual,
                    ok=ok,
                    reason="ok" if ok else "sha256_mismatch",
                )
            )
        except (FileNotFoundError, IntegrityViolation, OSError) as exc:
            results.append(
                IntegrityResult(
                    name=target.name,
                    path=target.relative_path,
                    expected_sha256=target.sha256,
                    actual_sha256=None,
                    ok=False,
                    reason=str(exc) or exc.__class__.__name__,
                )
            )

    return IntegrityReport(manifest_version=version, results=tuple(results))


def enforce_manifest(
    manifest_path: str | Path,
    *,
    root: str | Path,
    expected_manifest_owner_uid: int | None = None,
) -> IntegrityReport:
    """Fail closed unless every manifest artifact verifies."""
    report = verify_manifest(
        manifest_path,
        root=root,
        expected_manifest_owner_uid=expected_manifest_owner_uid,
    )
    if not report.ok:
        summary = ",".join(f"{item.name}:{item.reason}" for item in report.failures)
        raise IntegrityViolation(f"startup_integrity_failed:{summary}")
    return report
