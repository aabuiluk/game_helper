#!/usr/bin/env python3
"""Stellaris helper: Qt app to toggle Ironman and an overlay with cheat codes."""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

CRASH_LOG = Path(__file__).resolve().parent / "helper_crash.log"


def run_gui() -> int:
    from PySide6.QtWidgets import QApplication

    from main_window import MainWindow

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Stellaris Ironman Helper")
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception:
        CRASH_LOG.write_text(traceback.format_exc(), encoding="utf-8")
        print(f"Хелпер впав. Лог: {CRASH_LOG}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Stellaris Ironman Helper (Qt)")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("gui", "list", "unlock", "lock"),
        default="gui",
        help="gui за замовчуванням; unlock знімає Ironman, lock повертає Ironman і ачівки",
    )
    parser.add_argument("--file", type=Path, help="Конкретний .sav (інакше береться найсвіжіший)")
    args = parser.parse_args()

    if args.command == "gui":
        return run_gui()

    from stellaris_saves import (
        find_saves,
        format_save,
        inspect_save,
        latest_save,
        convert_save,
        stellaris_running,
    )

    try:
        if args.command == "list":
            saves = find_saves()
            if not saves:
                print("Сейви не знайдені.")
                return 1
            for save in saves:
                print(format_save(save))
                print("-" * 40)
            return 0

        save = inspect_save(args.file) if args.file else latest_save()
        enable = args.command == "lock"
        if stellaris_running():
            print("Увага: Stellaris зараз запущена. Краще закрити гру перед конвертацією.")
        target, backup = convert_save(save.path, enable)
        print(format_save(inspect_save(target)))
        print(f"Резервна копія: {backup}")
        return 0
    except Exception as error:
        print(f"Помилка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
