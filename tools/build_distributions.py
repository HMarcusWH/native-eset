#!/usr/bin/env python3
"""Offline PEP-517 backend build; does not install or claim unexecuted tool versions."""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('dist'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise SystemExit('Refusing to overwrite a populated distribution directory')
    os.chdir(root)
    # Setuptools can emit both supported artifacts without the optional build frontend.
    from setuptools import build_meta
    wheel = build_meta.build_wheel(str(out))
    sdist = build_meta.build_sdist(str(out))
    for name in ('build', 'src/native_eset.egg-info'):
        shutil.rmtree(root/name, ignore_errors=True)
    print(json.dumps({'status':'DISTRIBUTIONS_BUILT_NOT_CI_VALIDATED','wheel':wheel,'sdist':sdist,
                      'python':sys.version.split()[0], 'setuptools':importlib.metadata.version('setuptools')},sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
