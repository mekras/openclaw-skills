#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class ValidationError(Exception):
    pass


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def parse_skill_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationError(f"{skill_md}: missing frontmatter start")
    try:
        _, fm, _ = text.split("---\n", 2)
    except ValueError as exc:
        raise ValidationError(f"{skill_md}: malformed frontmatter block") from exc
    fields: dict[str, str] = {}
    for line in fm.strip().splitlines():
        if ":" not in line:
            raise ValidationError(f"{skill_md}: invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def discover_skill_dirs(target: Path) -> list[Path]:
    target = target.resolve()
    if not target.exists():
        raise ValidationError(f"{target}: path does not exist")
    if target.is_file():
        raise ValidationError(f"{target}: expected a skill directory or skills root")
    if (target / "SKILL.md").exists():
        return [target]
    skill_dirs = sorted(path.parent for path in target.rglob("SKILL.md"))
    if not skill_dirs:
        raise ValidationError(f"{target}: no skills with SKILL.md found")
    return skill_dirs


def ensure_list(value: object, name: str, path: Path) -> list[object]:
    if not isinstance(value, list):
        raise ValidationError(f"{path}: {name} must be a list")
    return value


def ensure_dict(value: object, name: str, path: Path) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: {name} must be an object")
    return value


def ensure_case_id_filter(case_ids: list[str], known_case_ids: set[str], label: str) -> None:
    missing = sorted(set(case_ids) - known_case_ids)
    if missing:
        raise ValidationError(f"{label}: unknown case id(s): {', '.join(missing)}")


def parse_case_filters(parser: argparse.ArgumentParser, args: argparse.Namespace) -> list[str]:
    filters: list[str] = []
    if getattr(args, "case_id", None):
        filters.extend(args.case_id)
    env_single = (Path.cwd().joinpath(".").anchor and None)
    del env_single
    return filters
