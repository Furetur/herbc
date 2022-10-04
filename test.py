import dataclasses
import io
import os.path
import subprocess
import sys
import traceback
from enum import Enum
from pathlib import Path
from typing import Union, List, Tuple
from contextlib import redirect_stdout

from main import run_compiler, RT_PATH, HERB_STD_PATH

test_data_dir = Path("test") / "data"
test_data_build = test_data_dir / "build"
build_dir = Path("build")
temp_program_path = build_dir / "testprog"
runtime_path: Path
herb_std_path: Path


class TestType(Enum):
    Positive = 0
    CompileTimeError = 1
    RuntimeError = 2
    IncorrectOutput = 3
    CompilerCrashed = 4


@dataclasses.dataclass()
class TestRun:
    path: Path
    expected_typ: TestType
    actual_typ: TestType
    stdout: str = ""
    stderr: str = ""

    def is_successful(self) -> bool:
        return self.expected_typ == self.actual_typ

    def __str__(self):
        if self.is_successful():
            return f"SUCCESS: {self.path}"
        else:
            msg = f"--- FAIL: {self.path}\n\texpected '{self.expected_typ.name}' but was '{self.actual_typ.name}'\n"
            if self.stdout != "":
                msg += f"- STDOUT:\n{self.stdout}\n- END STDOUT"
            if self.stderr != "":
                msg += f"- STDERR:\n{self.stderr}\n-END STDERR"
            return msg


@dataclasses.dataclass
class Test:
    path: Path
    typ: TestType

    def __init__(self, path: Path):
        assert path.is_file()
        self.path = path
        stem = path.stem
        if "_nc_" in stem:
            self.typ = TestType.CompileTimeError
        elif "nr_" in stem:
            self.typ = TestType.RuntimeError
        else:
            self.typ = TestType.Positive

    def run(self) -> TestRun:
        actual_typ, stdout, stderr = self.__run()
        return TestRun(path=self.path, expected_typ=self.typ, actual_typ=actual_typ, stdout=stdout, stderr=stderr)

    def __run(self) -> Tuple[TestType, str, str]:
        compiler_out = io.StringIO()
        with redirect_stdout(compiler_out):
            try:
                ok = run_compiler(self.path, temp_program_path)
            except Exception as e:
                return TestType.CompilerCrashed, "", traceback.format_exc()

        if not ok:
            return TestType.CompileTimeError, compiler_out.getvalue(), ""
        result = subprocess.run([], executable=temp_program_path, text=True, capture_output=True)
        ok = result.returncode == 0
        if not ok:
            return TestType.RuntimeError, result.stdout, result.stderr
        expected_output = self.__load_expected_stdout()
        if expected_output is None:
            return TestType.IncorrectOutput, "ERROR: Could not open stdout file", ""
        if result.stdout != expected_output:
            return TestType.IncorrectOutput, result.stdout, result.stderr
        return TestType.Positive, result.stdout, result.stderr

    def __load_expected_stdout(self) -> Union[str, None]:
        path = self.path.parent / (self.path.stem + ".stdout")
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")


def find_tests() -> List[Test]:
    return [Test(p) for p in test_data_dir.glob("*.herb")]


def main():
    global runtime_path
    runtime_path = Path(os.path.abspath(__file__)).parent / "runtime"

    build_dir.mkdir(exist_ok=True)

    print("TESTING STARTED\n")

    n_tests = 0
    n_passed = 0

    for test in find_tests():
        n_tests += 1
        result = test.run()
        if result.is_successful():
            n_passed += 1
        else:
            print(result, "\n")

    print(f"TOTAL {n_tests} | SUCCESS {n_passed} | FAIL {n_tests - n_passed}")
    if n_passed < n_tests:
        print("FAIL!")
        exit(1)
    else:
        print("SUCCESS")


if __name__ == "__main__":
    main()
