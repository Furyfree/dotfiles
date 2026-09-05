#!/usr/bin/env python3
"""One entry point for the small standalone test suites beside this file."""

import importlib.util
from pathlib import Path
import sys
import unittest


sys.dont_write_bytecode = True
suite = unittest.TestSuite()
for path in sorted(Path(__file__).parent.glob("*.py")):
    if path.name == Path(__file__).name:
        continue
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))

result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
