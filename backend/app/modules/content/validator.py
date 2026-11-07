import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


@dataclass(slots=True)
class PackValidationResult:
    valid: bool
    pack_key: str | None = None
    version: str | None = None
    question_count: int = 0
    manifest_sha256: str | None = None
    errors: list[str] = field(default_factory=list)


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _safe_pack_path(root: Path, relative_path: str) -> Path:
    candidate = PurePosixPath(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise ValueError(f"Unsafe content path: {relative_path}")
    resolved_root = root.resolve()
    resolved = (root / Path(*candidate.parts)).resolve()
    if resolved_root not in resolved.parents:
        raise ValueError(f"Content path escapes pack root: {relative_path}")
    if not resolved.is_file():
        raise ValueError(f"Content file not found: {relative_path}")
    return resolved


def validate_pack(
    pack_dir: Path,
    manifest_schema_path: Path,
    question_schema_path: Path,
) -> PackValidationResult:
    result = PackValidationResult(valid=False)
    try:
        manifest_path = _safe_pack_path(pack_dir, "manifest.json")
        manifest = _load_json(manifest_path)
        manifest_schema = _load_json(manifest_schema_path)
        question_schema = _load_json(question_schema_path)
        manifest_errors = sorted(
            Draft202012Validator(manifest_schema, format_checker=FormatChecker()).iter_errors(manifest),
            key=lambda error: list(error.path),
        )
        if manifest_errors:
            result.errors.extend(f"manifest: {'/'.join(map(str, e.path))}: {e.message}" for e in manifest_errors)
            return result

        result.pack_key = manifest["pack_key"]
        result.version = manifest["version"]
        result.manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        question_validator = Draft202012Validator(question_schema, format_checker=FormatChecker())
        actual_count = 0
        seen_question_keys: set[str] = set()
        seen_paths: set[str] = set()
        for entry in manifest["files"]:
            relative = entry["path"]
            if relative in seen_paths:
                result.errors.append(f"duplicate file entry: {relative}")
                continue
            seen_paths.add(relative)
            file_path = _safe_pack_path(pack_dir, relative)
            raw = file_path.read_bytes()
            if len(raw) != entry["bytes"]:
                result.errors.append(f"{relative}: byte count mismatch")
            if hashlib.sha256(raw).hexdigest().lower() != entry["sha256"].lower():
                result.errors.append(f"{relative}: SHA-256 mismatch")
            records = 0
            for line_number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                records += 1
                actual_count += 1
                try:
                    question = json.loads(line)
                except json.JSONDecodeError as exc:
                    result.errors.append(f"{relative}:{line_number}: invalid JSON ({exc.msg})")
                    continue
                errors = sorted(question_validator.iter_errors(question), key=lambda error: list(error.path))
                result.errors.extend(
                    f"{relative}:{line_number}: {'/'.join(map(str, error.path))}: {error.message}"
                    for error in errors
                )
                key = question.get("question_key") if isinstance(question, dict) else None
                if key in seen_question_keys:
                    result.errors.append(f"{relative}:{line_number}: duplicate question_key {key}")
                elif key:
                    seen_question_keys.add(key)
                if isinstance(question, dict):
                    option_keys = [option.get("key") for option in question.get("options", [])]
                    answer_key = question.get("answer_key", {}).get("option_key")
                    if len(option_keys) != len(set(option_keys)):
                        result.errors.append(f"{relative}:{line_number}: duplicate option keys")
                    if answer_key not in option_keys:
                        result.errors.append(f"{relative}:{line_number}: answer key does not match an option")
            if records != entry["records"]:
                result.errors.append(f"{relative}: record count mismatch")
        result.question_count = actual_count
        if actual_count != manifest["question_count"]:
            result.errors.append("manifest question_count does not match actual records")
        result.valid = not result.errors
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
        result.errors.append(str(exc))
    return result
