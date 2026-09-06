#!/usr/bin/env python3
"""Generate per-trait run files for species / pop group 357."""

from __future__ import annotations

from run_scripts import POP_357_EVENT_TRAITS, SCRIPTS_DIR, pop_357_effect_line


def main() -> None:
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    for item in POP_357_EVENT_TRAITS:
        path = SCRIPTS_DIR / item.filename
        path.write_text(pop_357_effect_line(item.trait_id) + "\n", encoding="utf-8")
        print(path.name)


if __name__ == "__main__":
    main()
