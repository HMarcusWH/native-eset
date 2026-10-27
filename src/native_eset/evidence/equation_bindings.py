"""Verify equation/source/function bindings without claiming that code satisfies physics."""
from __future__ import annotations
import hashlib
import importlib
import inspect
from pathlib import Path
from native_eset.serialization import read_json, resolve_regular_file


class EquationBindingError(ValueError):
    pass


def inspect_bindings(file:Path,root:Path)->dict:
    data=read_json(file)
    if data.get("schema")!="NATIVE_ESET_EQUATION_BINDINGS_V1":
        raise EquationBindingError("unsupported equation bindings")
    checks=[]
    bindings=data.get("bindings")
    if not isinstance(bindings,list) or not bindings:
        raise EquationBindingError("empty/malformed equation binding registry")
    seen=set()
    for b in bindings:
        if not isinstance(b,dict) or not b.get("equation_id") or b["equation_id"] in seen:
            raise EquationBindingError("invalid/duplicate equation binding")
        seen.add(b["equation_id"])
        if b.get("implementation_status")=="NOT_IMPLEMENTED_SOURCE_IMPORT_REQUIRED":
            if b.get("implementation") is not None:
                raise EquationBindingError("unimplemented equation binds to code")
            checks.append({"equation_id":b["equation_id"],"status":"NOT_IMPLEMENTED"})
            continue
        try:
            source=resolve_regular_file(root,b["source_path"])
        except ValueError as exc:
            raise EquationBindingError(str(exc)) from exc
        if not isinstance(b.get("implementation"),str) or not b["implementation"].startswith("native_eset."):
            raise EquationBindingError("only local native_eset implementations may be inspected")
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=b["source_sha256"]:
            raise EquationBindingError(f"wrong equation source file: {b['equation_id']}")
        parts=b["implementation"].split(".")
        found=False
        for n in range(len(parts)-1,0,-1):
            try:
                obj=importlib.import_module(".".join(parts[:n]))
                for part in parts[n:]:
                    obj=getattr(obj,part)
                location = inspect.getsourcefile(obj)
                if location is None or Path(location).resolve() != source.resolve():
                    raise EquationBindingError("implementation belongs to a different source file")
                if not callable(obj):
                    raise EquationBindingError("bound implementation is not callable")
                found=True
                break
            except (ModuleNotFoundError,AttributeError):
                continue
        if not found:
            raise EquationBindingError(f"missing implementation {b['implementation']}")
        checks.append({"equation_id":b["equation_id"],"status":"SOURCE_ID_AND_ATTRIBUTE_EXIST_NOT_PHYSICS_PROVED"})
    return {"status":"SOURCE_BINDINGS_CHECKED","bindings":checks}
