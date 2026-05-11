#!/usr/bin/env python3
"""Harness Evaluator — thin wrapper for pip-installed package.

When installed via pip, use: harness <command>
When running from source: python3 -m harness <command>
"""
import sys
import os

# Add src/ to path for development imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(os.path.dirname(_this_dir), "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from harness.cli import main
main()
