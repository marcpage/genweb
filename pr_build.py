#!/usr/bin/env python3

""" Script to run PR checks in parallel"""

import sys
import venv
import subprocess
import glob
import os
import re
import threading
import queue
import shutil
import time


def updated(file):
    """When was the file last updated, or 0 if does not exist"""
    return 0 if not os.path.isfile(file) else os.path.getmtime(file)


MINIMUM_TEST_COVERAGE = 9  # percent
COVERAGE_FLAGS = (
    "--show-missing --skip-covered --skip-empty --omit=financial_game/__main__.py"
)
PYTHON_SOURCE_DIR = "genweb"
PYTHON_SOURCES = [os.path.join(PYTHON_SOURCE_DIR, "*.py")]
LINT_SOURCES = [
    os.path.join(PYTHON_SOURCE_DIR, n)
    for n in ["generate_alpha_toc.py", "metaphone.py"]
]
REQUIREMENTS_PATH = "requirements.txt"
VENV_PATH = ".venv"
FLAKE8_DISABLES = [
    "E203",  # whitespace before ':'
    "W503",  # line break before binary operator
]
FLAKE8_FLAGS = "--max-line-length=100"
FLAKE8_FLAGS += f" --ignore={','.join(FLAKE8_DISABLES)}" if FLAKE8_DISABLES else ""
GITHUB_WORKFLOW = os.environ.get("GITHUB_WORKFLOW", "") == "CI"
ERROR_PREFIX = "##[error]" if GITHUB_WORKFLOW else "💥💥"
LINT_ERROR_PATTERN = re.compile(r"^(.*:.*:.*:)", re.MULTILINE)
PIP_QUIET = "" if GITHUB_WORKFLOW else "--quiet"
VENV_TIMESTAMP_FILE = os.path.join(VENV_PATH, "updated")
SKIP_VENV = "quick" in sys.argv or updated(VENV_TIMESTAMP_FILE) >= updated(
    REQUIREMENTS_PATH
)


def main():  # pylint: disable=too-many-branches,too-many-statements
    """PR script"""
    #####################################
    #
    #  Python venv
    #
    #####################################
    if not SKIP_VENV:
        github_log("##[group] Installing dependencies")
        github_log(f"##[command]python3 -m venv {VENV_PATH}")
        venv.create(VENV_PATH, symlinks=True, with_pip=True)
        github_log(f"##[command]pip3 install {PIP_QUIET} --upgrade pip")
        Start(f"pip install {PIP_QUIET} --upgrade pip").dump()
        github_log(
            f"##[command]pip3 install {PIP_QUIET} --requirement {REQUIREMENTS_PATH}"
        )
        Start(f"pip install {PIP_QUIET} --requirement {REQUIREMENTS_PATH}").dump()
        github_log("##[endgroup]")
        os.makedirs(os.path.split(VENV_TIMESTAMP_FILE)[0], exist_ok=True)

        with open(VENV_TIMESTAMP_FILE, "w", encoding="utf-8") as timestamp_file:
            timestamp_file.write("")

        os.utime(
            VENV_TIMESTAMP_FILE, (time.time(), os.path.getmtime(REQUIREMENTS_PATH))
        )

    #####################################
    #
    #  Start parallel processes
    #
    #####################################
    black_check = "--check" if len(sys.argv) == 1 else ""
    format_sources = expand_files(__file__, *PYTHON_SOURCES)
    lint_sources = expand_files(__file__, *LINT_SOURCES)

    github_log("##[group] Running black python source validation")
    github_log(f"##[command]python3 -m black {black_check} {format_sources}")
    black = Start(f"python3 -m black {black_check} {format_sources}", check=False)

    if black_check:  # if black is modifying code wait until it is done
        black.join()

    pylint = Start(
        f"pylint {lint_sources}",
        check=False,
        line_filter=lambda line: LINT_ERROR_PATTERN.sub(f"{ERROR_PREFIX}\\1", line),
    )
    flake8 = Start(
        f"flake8 {FLAKE8_FLAGS} {lint_sources}",
        check=False,
        line_filter=lambda line: LINT_ERROR_PATTERN.sub(f"{ERROR_PREFIX}\\1", line),
    )
    tests = Start(
        f"python3 -m coverage run --source={PYTHON_SOURCE_DIR} -m pytest", check=False
    )

    #####################################
    #
    #  black Python formatting / linting
    #
    #####################################
    return_code, duration = black.dump()
    return_codes = [return_code]
    github_log("##[endgroup]")

    if return_code != 0:
        sys.stdout.write(
            f"{ERROR_PREFIX}💥💥 Please run black on this source to reformat and resubmit 💥💥 \n"
        )
    else:
        sys.stdout.write(f"✅ black verification successful ({duration:0.3f} seconds)\n")

    #####################################
    #
    #  flake8 Python linting
    #
    #####################################
    github_log("##[group] Running flake8 python source validation")
    github_log(f"##[command]flake8 {FLAKE8_FLAGS} {lint_sources}")
    return_code, duration = flake8.dump()
    return_codes.append(return_code)
    github_log("##[endgroup]")

    if return_code != 0:
        sys.stdout.write(
            f"{ERROR_PREFIX}💥💥 Please fix the above flake8 errors and resubmit 💥💥 \n"
        )
    else:
        sys.stdout.write(
            f"✅ flake8 verification successful ({duration:0.3f} seconds)\n"
        )

    #####################################
    #
    #  Run Python unit tests
    #
    #####################################
    github_log("##[group] Running python unit tests")
    github_log(
        f"##[command]python3 -m coverage run --source={PYTHON_SOURCE_DIR} -m pytest"
    )
    return_code, duration = tests.dump()
    return_codes.append(return_code)
    github_log("##[endgroup]")

    if return_code != 0:
        sys.stdout.write(
            f"{ERROR_PREFIX}💥💥 Please fix the above test failures and resubmit 💥💥 \n"
        )
    else:
        sys.stdout.write(f"✅ unit tests passed ({duration:0.3f} seconds)\n")

    #####################################
    #
    #  pylint Python linting
    #
    #####################################
    github_log("##[group] Running pylint python source validation")
    github_log(f"##[command]pylint {lint_sources}")
    return_code, duration = pylint.dump()
    return_codes.append(return_code)
    github_log("##[endgroup]")

    if return_code != 0:
        sys.stdout.write(
            f"{ERROR_PREFIX}💥💥 Please fix the above pylint errors and resubmit 💥💥 \n"
        )
    else:
        sys.stdout.write(
            f"✅ pylint verification successful ({duration:0.3f} seconds)\n"
        )

    #####################################
    #
    #  Evaluate Python unit test coverage
    #
    #####################################

    github_log("##[group] Checking python unit test coverage")
    github_log(
        "##[command]python3 -m coverage report "
        + f"--fail-under={MINIMUM_TEST_COVERAGE} {COVERAGE_FLAGS}"
    )
    return_code, _ = Start(
        "python3 -m coverage report "
        + f"--fail-under={MINIMUM_TEST_COVERAGE} {COVERAGE_FLAGS}",
        check=False,
    ).dump()
    return_codes.append(return_code)
    github_log("##[endgroup]")

    if return_code != 0:
        sys.stdout.write(
            f"{ERROR_PREFIX}💥💥 Please bring test coverage to "
            + f"{MINIMUM_TEST_COVERAGE}% and resubmit 💥💥 \n"
        )
    else:
        sys.stdout.write("✅ sufficient test coverage\n")

    #####################################
    #
    #  Return failing status
    #
    #####################################
    if any(r != 0 for r in return_codes):
        sys.exit(sum(return_codes) if sum(return_codes) != 0 else 1)


class Start(threading.Thread):  # pylint: disable=too-many-instance-attributes
    """Start a command line executing in a python environment"""

    def __init__(
        self,
        command: str,
        virt_env: str = VENV_PATH,
        line_filter=None,
        check: bool = False,
    ):
        self.command = command
        self.venv = virt_env
        self.__check = check
        self.__messages = queue.Queue()
        self.__line_filter = (lambda x: x) if line_filter is None else line_filter
        self.return_code = None
        self.__process = None
        threading.Thread.__init__(self, daemon=True)
        self.start()
        self.start_time = time.perf_counter()
        self.duration = None

    def __stream(self, stream, name: str):
        for line in iter(stream.readline, ""):
            self.__messages.put((name, self.__line_filter(line)))

    def __start_stream(self, stream, name: str) -> threading.Thread:
        thread = threading.Thread(target=self.__stream, args=(stream, name))
        thread.start()
        return thread

    def dump(self):
        """While waiting for the process to complete, dump stderr and stdout"""
        streams = {"out": sys.stdout, "err": sys.stderr}
        sys.stdout.flush()
        sys.stderr.flush()

        while (
            self.__process is None
            or self.__messages.qsize() > 0
            or self.__process.poll() is None
        ):
            try:
                message = self.__messages.get(timeout=0.100)
                streams[message[0]].write(message[1])

            except queue.Empty:
                pass

        sys.stdout.flush()
        sys.stderr.flush()
        assert (
            not self.__check or self.return_code == 0
        ), f"Return code = {self.return_code}"
        self.join()
        return self.return_code, self.duration

    def run(self):
        """Start the command line running and start the io threads"""
        shell = shutil.which("bash")

        with subprocess.Popen(
            (shell, "-c", f"source .venv/bin/activate && {self.command}"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        ) as self.__process:
            self.__start_stream(self.__process.stdout, "out")
            self.__start_stream(self.__process.stderr, "err")
            self.return_code = self.__process.wait()
            assert (
                not self.__check or self.return_code == 0
            ), f"Return code = {self.return_code}"

        self.duration = time.perf_counter() - self.start_time


def expand_files(*file_list):
    """takes a list of file patterns and expands them into files separated by space"""
    return " ".join([p for f in file_list for p in glob.glob(f)])


def github_log(text: str):
    """Log if we're in a GitHub action"""
    if GITHUB_WORKFLOW:
        sys.stdout.write(text + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
