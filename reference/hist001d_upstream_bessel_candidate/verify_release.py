#!/usr/bin/env python3
"""HIST-001D PR58 release verifier: externally attested source execution ONLY.

The old locally rehashable manifest-based full replay was vulnerable to a
substituted independent checker. This wrapper never emits proof PASS without
a separate externally supplied whole-ZIP SHA and clean source reexecution.
"""
import runpy
from pathlib import Path

if __name__=='__main__':
    runpy.run_path(str(Path(__file__).with_name('attested_replay_v1r2.py')),
                   run_name='__main__')
