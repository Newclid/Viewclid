from typing import Any

from newclid_backend.settings import MAX_OUTPUT_CHARS


def _truncate_output(output: str | None) -> str:
    if output is None:
        return ""
    if len(output) <= MAX_OUTPUT_CHARS:
        return output
    return output[-MAX_OUTPUT_CHARS:]


def _to_run_info_dict(run_info: Any) -> dict[str, Any] | None:
    if run_info is None:
        return None
    return run_info.model_dump()


def _as_str_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"Custom rule field '{field_name}' must be a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"Custom rule field '{field_name}' must contain only strings")
    return tuple(value)


def _build_custom_rule_fields(
    custom_theorems: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rule_kwargs: list[dict[str, Any]] = []
    for theorem in custom_theorems:
        name = theorem.get("name")
        if not isinstance(name, str):
            raise ValueError("Custom theorem field 'name' must be a string")
        description = theorem.get("description") or name
        if not isinstance(description, str):
            raise ValueError("Custom theorem field 'description' must be a string")
        rule_kwargs.append(
            {
                "id": name,
                "description": description,
                "premises_txt": _as_str_tuple(theorem.get("premises"), "premises"),
                "conclusions_txt": _as_str_tuple(
                    theorem.get("conclusions"), "conclusions"
                ),
            }
        )
    return rule_kwargs
