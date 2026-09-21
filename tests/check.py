"""One entry point for the small standalone test suites beside this file.

Suites run in parallel worker processes (JOBS, default: cpu_count); the
report stays deterministic, ordered by module name, with failure traces
aggregated after the summary. JOBS=1 keeps the serial single-process path.
"""

import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ProcessPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

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
    skipped = [(str(test), reason) for test, reason in result.skipped]
    return path, result.wasSuccessful(), time.monotonic() - started, result.testsRun, traces, skipped


def main():
    paths = sorted(str(p) for p in HERE.glob("*.py") if p.name != Path(__file__).name)
    jobs = int(os.environ.get("JOBS") or os.cpu_count() or 1)
    if jobs <= 1:
        results = [run_suite(path) for path in paths]
    else:
        with ProcessPoolExecutor(max_workers=min(jobs, len(paths))) as pool:
            results = list(pool.map(run_suite, paths))
    for path, ok, seconds, count, _, skipped in results:
        label = "FAIL" if not ok else "SKIP" if skipped and len(skipped) == count else "ok"
        print(f"{label:4} {seconds:6.1f}s  {count:3d} tests  {len(skipped):3d} skipped  {Path(path).name}")
        for test, reason in skipped:
            print(f"  SKIP {test}: {reason}")
    failures = [result for result in results if not result[1]]
    for path, _, _, _, traces, _ in failures:
        for trace in traces:
            print(f"\n===== {Path(path).name} =====\n{trace}")
    slowest = max((result[2] for result in results), default=0.0)
    skipped_count = sum(len(result[5]) for result in results)
    print(f"\n{len(results)} suites, {len(failures)} failed, {skipped_count} tests skipped, slowest {slowest:.1f}s")
    return 1 if failures else 0


def self_test():
    with tempfile.TemporaryDirectory(prefix="dotfiles-check-runner-") as temp:
        root = Path(temp)
        runner = root / "check.py"
        runner.write_text(Path(__file__).read_text())
        (root / "a_pass.py").write_text(
            "import unittest\nclass Pass(unittest.TestCase):\n"
            "    def test_pass(self): self.assertEqual(2 + 2, 4)\n")
        (root / "b_skip.py").write_text(
            "import unittest\nclass Skip(unittest.TestCase):\n"
            "    def test_skip(self): self.skipTest('fixture validator unavailable')\n")
        for failing in (False, True):
            if failing:
                (root / "c_fail.py").write_text(
                    "import unittest\nclass Fail(unittest.TestCase):\n"
                    "    def test_fail(self): self.fail('fixture failure')\n")
            for jobs in ("1", "2"):
                result = subprocess.run(
                    [sys.executable, str(runner)], cwd=root,
                    env=os.environ | {"JOBS": jobs}, capture_output=True, text=True, timeout=30, check=False)
                assert result.returncode == int(failing), result.stdout + result.stderr
                assert "SKIP" in result.stdout and "fixture validator unavailable" in result.stdout
                assert "1 tests skipped" in result.stdout, result.stdout
                assert result.stdout.index("a_pass.py") < result.stdout.index("b_skip.py")
                if failing:
                    assert "fixture failure" in result.stdout and "1 failed" in result.stdout
        print("Runner reporting checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(self_test() if sys.argv[1:] == ["--self-test"] else main())
