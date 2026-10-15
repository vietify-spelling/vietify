"""Entry point for the packaged desktop app.

``--self-test`` converts a sample and runs the bundled espeak-ng, then exits.
It is meant for checking a build on a new machine.
"""

import sys


def self_test() -> int:
    from vietify.espeak_runtime import bundled_dir, espeak_binary, espeak_data_args, espeak_env
    from vietify.main import text_to_vietify_all
    import subprocess

    ipa, strong, weak = text_to_vietify_all("Bonjour tout le monde", "fr")
    print("IPA:   ", ipa)
    print("strong:", strong)
    print("weak:  ", weak)
    print("bundle:", bundled_dir())

    from vietify.tts import VOICES

    binary = espeak_binary()
    ok = bool(strong)
    for voice in sorted(set(VOICES.values())):
        result = subprocess.run(
            [binary, *espeak_data_args(), "--stdout", "-v", voice, "test"],
            env=espeak_env(), capture_output=True,
        )
        good = result.returncode == 0 and len(result.stdout) > 0
        ok = ok and good
        print(f"espeak-ng voice {voice:6} {'ok' if good else 'FAILED'}")
    print("SELF-TEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    from vietify.gui import main

    raise SystemExit(main())
