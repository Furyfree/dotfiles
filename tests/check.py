#!/usr/bin/env python3
"""One entry point for the small standalone test suites beside this file.

Suites run in parallel worker processes (JOBS, default: cpu_count); the
report stays deterministic, ordered by module name, with failure traces
aggregated after the summary. JOBS=1 keeps the serial single-process path.
"""

import importlib.util
from concurrent.futures import ProcessPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import sys
import time
import unittest


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load_tests(path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def run_suite(path):
    stream = io.StringIO()
    started = time.monotonic()
    with redirect_stdout(stream), redirect_stderr(stream):
        result = unittest.TextTestRunner(verbosity=0, stream=stream).run(load_tests(Path(path)))
    traces = [trace for _, trace in result.failures + result.errors]
    return path, result.wasSuccessful(), time.monotonic() - started, result.testsRun, traces


def main():
    paths = sorted(str(p) for p in HERE.glob("*.py") if p.name != Path(__file__).name)
    jobs = int(os.environ.get("JOBS") or os.cpu_count() or 1)
    if jobs <= 1:
        results = [run_suite(path) for path in paths]
    else:
        with ProcessPoolExecutor(max_workers=min(jobs, len(paths))) as pool:
            results = list(pool.map(run_suite, paths))
    for path, ok, seconds, count, _ in results:
        print(f"{'ok  ' if ok else 'FAIL'} {seconds:6.1f}s  {count:3d} tests  {Path(path).name}")
    failures = [result for result in results if not result[1]]
    for path, _, _, _, traces in failures:
        for trace in traces:
            print(f"\n===== {Path(path).name} =====\n{trace}")
    slowest = max((result[2] for result in results), default=0.0)
    print(f"\n{len(results) - len(failures)}/{len(results)} suites passed, slowest {slowest:.1f}s")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
