#!/usr/bin/env python3
"""HIST001D D120 v1r2: full replay only via externally pinned attestor.

The old v1r1 self-manifest consistency check was NOT sufficient to establish
executed local verifier provenance: both source and local manifest could be
substituted. All source-bound replay requests now require an external whole-ZIP
SHA-256 and use the attested clean-extraction script directly.
"""
from __future__ import annotations
import sys
from attested_replay_v1r2 import main

if __name__ == '__main__':
    sys.exit(main())
