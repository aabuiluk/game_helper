#!/usr/bin/env python3
"""One asteroid per orbital resource, orbit 250, equal spacing, 500 each.

Select the system's star, then: run asteroid_belt_19.txt
Does not wipe existing bodies.
"""

from __future__ import annotations

from write_supersystem import (
    OUT,
    split_planet_effects,
    wrap_system,
    write_run,
)

ORBIT = 250
ASTEROID_SIZE = 5

# name, deposit effects that sum to 500 of that one resource.
# Unity deposits are only +3, so that asteroid is 501.
ASTEROIDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Energy", ("while = { count = 50 add_deposit = d_energy_10 }",)),
    ("Minerals", ("while = { count = 50 add_deposit = d_minerals_10 }",)),
    ("Food", ("while = { count = 50 add_deposit = d_food_10 }",)),
    ("Alloys", ("while = { count = 20 add_deposit = d_alloys_25 }",)),
    (
        "Goods",
        ("while = { count = 250 add_deposit = d_consumer_goods_obsessional_directive }",),
    ),
    ("Trade", ("while = { count = 50 add_deposit = d_trade_value_10 }",)),
    ("Gases", ("while = { count = 100 add_deposit = d_exotic_gases_5 }",)),
    ("Crystals", ("while = { count = 100 add_deposit = d_rare_crystals_5 }",)),
    ("Motes", ("while = { count = 100 add_deposit = d_volatile_motes_5 }",)),
    ("Living_Metal", ("while = { count = 500 add_deposit = d_living_metal_deposit }",)),
    (
        "Artifacts",
        (
            "while = { count = 166 add_deposit = d_artifacts_mining_3 }",
            "add_deposit = d_artifacts_mining_1",
            "add_deposit = d_artifacts_mining_1",
        ),
    ),
    (
        "Nanites",
        (
            "while = { count = 19 add_deposit = d_nanite_harvester_deposit_large }",
            "while = { count = 8 add_deposit = d_nanite_harvester_deposit_regular }",
            "while = { count = 8 add_deposit = d_nanite_harvester_deposit }",
        ),
    ),
    ("Physics", ("while = { count = 50 add_deposit = d_physics_10 }",)),
    (
        "Society",
        (
            "while = { count = 33 add_deposit = d_society_15 }",
            "add_deposit = d_society_5",
        ),
    ),
    ("Engineering", ("while = { count = 50 add_deposit = d_engineering_10 }",)),
    ("Unity", ("while = { count = 167 add_deposit = d_vast_unity_deposit }",)),
    ("Dark_Matter", ("while = { count = 50 add_deposit = d_dark_matter_deposit_10 }",)),
    ("Zro", ("while = { count = 100 add_deposit = d_zro_deposit_5 }",)),
    (
        "Astral",
        (
            "while = { count = 166 add_deposit = d_astral_threads_deposit_3 }",
            "add_deposit = d_astral_threads_deposit_1",
            "add_deposit = d_astral_threads_deposit_1",
        ),
    ),
)


def angle_token(index: int, count: int) -> str:
    value = index * 360 / count
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return text or "0"


def spawn_asteroid(flag: str, angle: str) -> str:
    return wrap_system(
        "spawn_planet = { class = pc_asteroid location = star orbit_location = yes "
        f"orbit_distance_offset = {ORBIT} orbit_angle_offset = {angle} "
        f"size = {ASTEROID_SIZE} has_ring = no "
        "init_effect = { "
        f"set_planet_flag = {flag} set_planet_size = {ASTEROID_SIZE} "
        "prevent_anomaly = yes } }"
    )


def rename_asteroid(flag: str, name: str) -> str:
    return wrap_system(
        "random_system_planet = { "
        f"limit = {{ has_planet_flag = {flag} }} set_name = {name} }}"
    )


def build_lines() -> list[str]:
    count = len(ASTEROIDS)
    lines: list[str] = []
    for i, (name, deposits) in enumerate(ASTEROIDS):
        flag = f"ss_belt_{i + 1}"
        lines.append(spawn_asteroid(flag, angle_token(i, count)))
        lines.append(rename_asteroid(flag, name))
        lines.extend(split_planet_effects(flag, list(deposits)))
    return lines


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lines = build_lines()
    write_run("asteroid_belt_19.txt", "\n".join(lines) + "\n")
    path = OUT / "asteroid_belt_19.txt"
    print(
        f"wrote {path.name} ({len(lines)} commands, orbit={ORBIT}, "
        f"asteroids={len(ASTEROIDS)})"
    )


if __name__ == "__main__":
    main()
