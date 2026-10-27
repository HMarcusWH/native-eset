"""CLASS reference boundary is intentionally disabled until a pinned upstream replay.

A successful ``Class.compute()`` without exported, checked observables is not a
usable reference result. Import this adapter in CTRL-001 with a specific source pin.
"""
from typing import Any


def class_reference_run(parameters: dict[str, Any]) -> dict[str, Any]:
    raise NotImplementedError(
        "CLASS_REFERENCE_NOT_IMPLEMENTED_SOURCE_LOCK_REQUIRED: "
        "Pin verified CLASS source and export real computed/compared arrays in CTRL-001"
    )
