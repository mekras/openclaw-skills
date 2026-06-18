#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from apm_skill_utils import (
    ValidationError,
    discover_skill_dirs,
    ensure_dict,
    ensure_list,
    load_json,
    parse_skill_frontmatter,
)


def validate_result_file(skill_dir: Path) -> int:
    skill_md = skill_dir / "SKILL.md"
    fields = parse_skill_frontmatter(skill_md)
    expected_name = fields.get("name")
    if not expected_name:
        raise ValidationError(f"{skill_md}: missing name in frontmatter")

    path = skill_dir / "evals" / "result-scenarios.json"
    if not path.exists():
        raise ValidationError(f"{path}: missing result scenarios file")

    data = ensure_dict(load_json(path), "root", path)
    if data.get("skill_name") != expected_name:
        raise ValidationError(
            f"{path}: skill_name {data.get('skill_name')!r} does not match {expected_name!r}"
        )

    source_basis = ensure_list(data.get("source_basis"), "source_basis", path)
    if not source_basis:
        raise ValidationError(f"{path}: source_basis must not be empty")

    cases = ensure_list(data.get("cases"), "cases", path)
    if not cases:
        raise ValidationError(f"{path}: cases must not be empty")

    seen_ids: set[str] = set()
    for index, case in enumerate(cases, start=1):
        case_dict = ensure_dict(case, f"cases[{index}]", path)
        for key in ("id", "prompt", "evaluation_surface"):
            value = case_dict.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"{path}: cases[{index}].{key} must be a non-empty string")
        for key in ("application_evidence", "assertions", "must_not"):
            values = ensure_list(case_dict.get(key), f"cases[{index}].{key}", path)
            if not values:
                raise ValidationError(f"{path}: cases[{index}].{key} must not be empty")
        for key in ("expected_output", "oracle", "negative_control"):
            ensure_dict(case_dict.get(key), f"cases[{index}].{key}", path)
        case_id = case_dict["id"]
        if case_id in seen_ids:
            raise ValidationError(f"{path}: duplicate case id {case_id!r}")
        seen_ids.add(case_id)
    return len(cases)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate result scenario evals for APM skills.")
    parser.add_argument("target", nargs="?", default=".apm/skills")
    args = parser.parse_args()

    skill_dirs = discover_skill_dirs(Path(args.target))
    total_cases = 0
    for skill_dir in skill_dirs:
        total_cases += validate_result_file(skill_dir)
    print(f"validated result evals: {len(skill_dirs)} skill(s), {total_cases} case(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
