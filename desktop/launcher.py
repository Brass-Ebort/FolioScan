"""Entry point; keeps automated packaging checks silent even on import failure."""

import sys

if __name__ == "__main__":
    try:
        from app import main

        main()
    except Exception:
        if "--self-test" in sys.argv:
            import json, traceback
            from pathlib import Path

            Path(sys.argv[sys.argv.index("--self-test") + 1]).write_text(
                json.dumps({"ok": False, "error": traceback.format_exc()}, indent=2),
                encoding="utf-8",
            )
            raise SystemExit(1)
        raise
