#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from apm_skill_utils import ValidationError, discover_skill_dirs, ensure_case_id_filter, ensure_dict, ensure_list, load_json


def read_case_filters(args: argparse.Namespace) -> list[str]:
    case_ids: list[str] = []
    if args.case_id:
        case_ids.extend(args.case_id)
    env_single = os.environ.get("APM_EVAL_CASE_ID")
    if env_single:
        case_ids.append(env_single)
    env_many = os.environ.get("APM_EVAL_CASE_IDS")
    if env_many:
        case_ids.extend([item.strip() for item in env_many.split(",") if item.strip()])
    return case_ids


def collect_cases(skill_dir: Path) -> dict[str, list[str]]:
    triggers_path = skill_dir / "evals" / "triggers.json"
    results_path = skill_dir / "evals" / "result-scenarios.json"

    trigger_cases = ensure_list(ensure_dict(load_json(triggers_path), "root", triggers_path).get("cases"), "cases", triggers_path)
    result_cases = ensure_list(ensure_dict(load_json(results_path), "root", results_path).get("cases"), "cases", results_path)
    return {
        "trigger": [ensure_dict(case, "case", triggers_path)["id"] for case in trigger_cases],
        "result": [ensure_dict(case, "case", results_path)["id"] for case in result_cases],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic eval selection for APM skills.")
    parser.add_argument("target", nargs="?", default=".apm/skills")
    parser.add_argument("--case-id", action="append", default=[])
    args = parser.parse_args()

    skill_dirs = discover_skill_dirs(Path(args.target))
    case_filters = read_case_filters(args)

    known_case_ids: set[str] = set()
    selected_trigger = 0
    selected_result = 0

    for skill_dir in skill_dirs:
        case_map = collect_cases(skill_dir)
        known_case_ids.update(case_map["trigger"])
        known_case_ids.update(case_map["result"])

    if case_filters:
        ensure_case_id_filter(case_filters, known_case_ids, "run-skill-evals")

    for skill_dir in skill_dirs:
        case_map = collect_cases(skill_dir)
        trigger_ids = case_map["trigger"]
        result_ids = case_map["result"]
        if case_filters:
            trigger_ids = [case_id for case_id in trigger_ids if case_id in case_filters]
            result_ids = [case_id for case_id in result_ids if case_id in case_filters]
        selected_trigger += len(trigger_ids)
        selected_result += len(result_ids)

    if case_filters and selected_trigger + selected_result == 0:
        raise ValidationError("run-skill-evals: no matching cases selected")

    mode = "selected" if case_filters else "full"
    print(
        f"deterministic eval run ok: mode={mode}, skills={len(skill_dirs)}, "
        f"trigger_cases={selected_trigger}, result_cases={selected_result}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
