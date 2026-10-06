from pathlib import Path
import subprocess
import sys


TEST_DIR = Path(__file__).resolve().parent
MAIN_PY = TEST_DIR / "main.py"
TESTCASES_DIR = TEST_DIR / "testcases"
RESULT_DIR = TEST_DIR / "generatedResult"


def run_main(text: str, language: str, mode: str) -> str | None:
    """
    Run main.py and return stdout.
    Return None when conversion fails.
    """

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(MAIN_PY),
                "-l",
                language,
                "-m",
                mode,
                text,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            print(
                f"[ERROR] language={language!r}, mode={mode!r}, "
                f"text={text!r}\n{result.stderr.strip()}"
            )
            return None

        return result.stdout.rstrip("\r\n")

    except OSError as error:
        print(
            f"[ERROR] Could not run main.py: "
            f"language={language!r}, mode={mode!r}, error={error}"
        )
        return None


def process_file(input_file: Path, language: str) -> None:
    """
    Process one txt file.

    Every non-empty line in input file is treated as one test case.
    """

    relative_path = input_file.relative_to(TESTCASES_DIR)

    output_file = RESULT_DIR / relative_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"[FILE] {relative_path}")

    output_lines = []

    with input_file.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            text = raw_line.rstrip("\r\n")

            # Skip empty lines.
            if not text.strip():
                continue

            print(f"  [{line_number}] {text}")

            # Original text.
            output_lines.append(text)

            # IPA.
            ipa = run_main(text, language, "ipa")

            if ipa is not None:
                output_lines.append(ipa)

            # Strong Vietify.
            strong = run_main(text, language, "strong")

            if strong is not None:
                output_lines.append(strong)
            else:
                output_lines.append("")

            # Weak Vietify.
            weak = run_main(text, language, "weak")

            if weak is not None:
                output_lines.append(weak)
            else:
                output_lines.append("")

    output_file.write_text(
        "\n".join(output_lines) + "\n",
        encoding="utf-8",
    )

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