from pathlib import Path
import subprocess
import sys


TEST_DIR = Path(__file__).resolve().parent
MAIN_PY = TEST_DIR.parent / "main.py"
TESTCASES_DIR = TEST_DIR / "testcases"
RESULT_DIR = TEST_DIR / "generatedResult"


def process_file(input_file: Path, language: str) -> None:
    """
    Process one txt file; every non-empty line is one test case.
    """

    relative_path = input_file.relative_to(TESTCASES_DIR)

    output_file = RESULT_DIR / relative_path
    print(f"[FILE] {relative_path}")

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(MAIN_PY),
                "-l",
                language,
                "--input-file",
                str(input_file),
                "--output-file",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        print(f"  [ERROR] Could not run main.py: {error}")
        return

    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr.strip()}")
        return

    print(f"  -> {output_file.relative_to(TEST_DIR)}")


def main() -> None:
    if not TESTCASES_DIR.exists():
        raise FileNotFoundError(
            f"Testcases directory does not exist: {TESTCASES_DIR}"
        )

    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    # testcases/
    #   en-us/
    #       test1.txt
    #       test2.txt
    #   fr/
    #       test1.txt
    #
    # generatedResult/
    #   en-us/
    #       test1.txt
    #       test2.txt
    #   fr/
    #       test1.txt

    for language_dir in sorted(TESTCASES_DIR.iterdir()):
        if not language_dir.is_dir():
            continue

        language = language_dir.name

        for input_file in sorted(language_dir.rglob("*.txt")):
            process_file(input_file, language)


if __name__ == "__main__":
    main()