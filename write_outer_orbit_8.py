#!/usr/bin/env python3
"""Outer ring: 8 size-30 worlds equally spaced (ecu / gaia alternating).

Select the system's star, then: run outer_orbit_8.txt
Does not wipe existing bodies. One ring just inside a typical outer dotted bound.
"""

from __future__ import annotations

from write_supersystem import (
    OUT,
    PLANET_SIZE,
    ecu_effects,
    gaia_effects,
    rename_flag_effect,
    spawn_planet_line,
    split_planet_effects,
    write_run,
)

OUTER_ORBIT = 250
PLANET_COUNT = 8


def build_lines() -> list[str]:
    if 360 % PLANET_COUNT != 0:
        raise ValueError("PLANET_COUNT must divide 360 for equal spacing")
    step = 360 // PLANET_COUNT
    lines: list[str] = []
    ecu_n = 0
    gaia_n = 0
    for i in range(PLANET_COUNT):
        angle = i * step
        # Через один: еку, гая, еку, гая…
        if i % 2 == 0:
            ecu_n += 1
            name = f"Outer Ecu {ecu_n}"
            flag = f"ss_outer_ecu_{ecu_n}"
            class_id = "pc_city"
            effects = ecu_effects()
        else:
            gaia_n += 1
            name = f"Outer Gaia {gaia_n}"
            flag = f"ss_outer_gaia_{gaia_n}"
            class_id = "pc_gaia"
            effects = gaia_effects(gaia_n - 1)
        lines.append(spawn_planet_line(class_id, flag, OUTER_ORBIT, angle, PLANET_SIZE))
        lines.append(rename_flag_effect(flag, name))
        lines.extend(split_planet_effects(flag, effects))
    return lines


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lines = build_lines()
    write_run("outer_orbit_8.txt", "\n".join(lines) + "\n")
    path = OUT / "outer_orbit_8.txt"
    print(
        f"wrote {path.name} ({len(lines)} commands, orbit={OUTER_ORBIT}, "
        f"4 ecu + 4 gaia size {PLANET_SIZE})"
    )


if __name__ == "__main__":
    main()
