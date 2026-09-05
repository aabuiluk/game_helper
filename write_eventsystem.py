#!/usr/bin/env python3
"""Neighbor event-system: 16 uncolonized worlds with colony-event hooks.

Select the super-system star (or any star), then: run eventsystem.txt
Spawns a hyperlane-linked system. Planets stay unowned. Country 0 gets the citadel.

Does not complete event chains, archaeology, rifts, or ruined mega repairs.
Does not research_all_technologies.
"""

from __future__ import annotations

from pathlib import Path

from write_supersystem import (
    MAX_CONSOLE_LINE,
    OUT,
    RUNNER,
    player_scope,
)

# 4 rings × 4, packed next to the super-system style.
ORBITS: tuple[tuple[int, int], ...] = tuple(
    (distance, (36 if ring % 2 else 0) + i * 90)
    for ring, distance in enumerate((40, 64, 88, 112))
    for i in range(4)
)

# One hook per world. Modifiers that colony_mod.161 checks fire on year 1.
# Others become eligible on the vanilla 2-year colony pulse. Archaeology is
# immediately excavable. Do not set colony_event flags (that would block chains).
PLANETS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "EV_Subterra",
        "pc_gaia",
        "ss_ev_subterra",
        "",
        "site_buried_deep",
    ),
    (
        "EV_Titanic",
        "pc_continental",
        "ss_ev_titanic",
        "add_modifier = { modifier = titanic_life days = -1 } "
        "add_deposit = d_titanic_life_blocker",
        "site_hunting_ground",
    ),
    (
        "EV_Forests",
        "pc_tropical",
        "ss_ev_forests",
        "",
        "site_fumongus_dig",
    ),
    (
        "EV_Terraform",
        "pc_ocean",
        "ss_ev_terraform",
        "",
        "site_warmer_climates",
    ),
    (
        "EV_Doorway",
        "pc_continental",
        "ss_ev_doorway",
        "",
        "site_echoes_inside",
    ),
    (
        "EV_Vault",
        "pc_nuked",
        "ss_ev_vault",
        "",
        "site_command_center",
    ),
    (
        "EV_Robot",
        "pc_relic",
        "ss_ev_robot",
        "",
        "site_ancient_robot_world",
    ),
    (
        "EV_Labyrinth",
        "pc_continental",
        "ss_ev_labyrinth",
        "",
        "site_hidden_lab_a",
    ),
    (
        "EV_Snow",
        "pc_desert",
        "ss_ev_snow",
        "",
        "site_ice_trauma",
    ),
    (
        "EV_Canopy",
        "pc_tropical",
        "ss_ev_canopy",
        "",
        "site_transformation_dig",
    ),
    (
        "EV_Nemma",
        "pc_ocean",
        "ss_ev_nemma",
        "",
        "site_fossilized_jellyfish",
    ),
    (
        "EV_Blossoms",
        "pc_savannah",
        "ss_ev_blossoms",
        "",
        "site_star_petal",
    ),
    (
        "EV_Factory",
        "pc_continental",
        "ss_ev_factory",
        "",
        "site_robot_debris",
    ),
    (
        "EV_Magnetic",
        "pc_tundra",
        "ss_ev_magnetic",
        "add_modifier = { modifier = strong_magnetic_field days = -1 }",
        "site_target_from_orbit",
    ),
    (
        "EV_Hallucinogen",
        "pc_continental",
        "ss_ev_hallucinogen",
        "add_modifier = { modifier = atmospheric_hallucinogen days = -1 }",
        "site_deja_vu_dig",
    ),
    (
        "EV_Crystals",
        "pc_arctic",
        "ss_ev_crystals",
        "",
        "city_of_bones",
    ),
)

RUINED_MEGAS: tuple[tuple[str, int, int], ...] = (
    ("think_tank_ruined", 28, 50),
    ("spy_orb_ruined", 32, 140),
    ("mega_art_installation_ruined", 36, 230),
    ("gateway_ruined", 52, 320),
)


def wrap_last(inner: str) -> str:
    return f"effect last_created_system = {{ {inner} }}"


def spawn_neighbor() -> str:
    return (
        "effect solar_system = { spawn_system = { min_distance = 10 max_distance = 16 "
        "max_jumps = 0 initializer = basic_init_01 hyperlane = yes is_discovered = yes } "
        "last_created_system = { set_star_flag = ss_eventsystem set_name = SS_Eventworlds "
        "if = { limit = { NOT = { has_hyperlane_to = prev } } "
        "add_hyperlane = { from = this to = prev } } } }"
    )


def wipe_new_system() -> list[str]:
    stations = wrap_last(
        "star = { if = { limit = { is_colony = yes } destroy_colony = yes } } "
        "every_system_megastructure = { remove_megastructure = this } "
        "every_system_ambient_object = { destroy_ambient_object = this } "
        "every_fleet_in_system = { limit = { OR = { "
        "is_ship_class = shipclass_starbase "
        "is_ship_class = shipclass_mining_station "
        "is_ship_class = shipclass_research_station "
        "is_ship_class = shipclass_military_station } } "
        "delete_fleet = this }"
    )
    planets = wrap_last(
        "every_system_planet = { limit = { is_star = no } "
        "if = { limit = { exists = orbital_station } "
        "orbital_station = { delete_fleet = this } } "
        "if = { limit = { is_colony = yes } destroy_colony = yes } "
        "remove_planet = yes }"
    )
    return [stations, planets]


def wrap_last_player(inner: str) -> str:
    return "effect { " + player_scope() + " last_created_system = { " + inner + " } }"


def citadel() -> str:
    return wrap_last_player(
        "if = { limit = { exists = starbase } "
        "starbase = { fleet = { delete_fleet = this } } } "
        "create_starbase = { "
        f"size = starbase_citadel owner = {RUNNER} }}"
    )


def spawn_planet(
    class_id: str,
    flag: str,
    distance: int,
    angle: int,
    extra: str,
) -> str:
    more = f" {extra}" if extra else ""
    return wrap_last(
        f"spawn_planet = {{ class = {class_id} location = star orbit_location = yes "
        f"orbit_distance_offset = {distance} orbit_angle_offset = {angle} "
        f"size = 78 has_ring = no "
        f"init_effect = {{ set_planet_flag = {flag} set_planet_size = 78 "
        f"prevent_anomaly = yes{more} }} }}"
    )


def finish_planet(flag: str, name: str, site: str) -> str:
    return wrap_last(
        "random_system_planet = { "
        f"limit = {{ has_planet_flag = {flag} }} set_name = {name} "
        f"create_archaeological_site = {site} }}"
    )


def spawn_rift() -> str:
    # Unexplored rift. No rewards, no completion flags.
    return wrap_last(
        "spawn_astral_rift = { random_pos = yes orbit_angle = 360 spawn_sound = no }"
    )


def spawn_ruined(type_id: str, distance: int, angle: int) -> str:
    return wrap_last_player(
        "spawn_megastructure = { "
        f"type = {type_id} planet = prev owner = {RUNNER} "
        f"orbit_distance = {distance} orbit_angle = {angle} }}"
    )


def survey() -> str:
    return wrap_last_player(
        "every_system_planet = { "
        f"set_surveyed = {{ surveyed = yes surveyor = {RUNNER} }} }}"
    )


def write_run(name: str, lines: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if len(stripped) > MAX_CONSOLE_LINE:
            raise ValueError(
                f"{name}:{i}: рядок {len(stripped)} символів, консоль обріже "
                f"(ліміт {MAX_CONSOLE_LINE}): {stripped[:80]}"
            )
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_lines() -> list[str]:
    if len(PLANETS) != 16 or len(ORBITS) != 16:
        raise ValueError("need 16 planets and 16 orbits")
    lines = [spawn_neighbor()]
    lines.extend(wipe_new_system())
    lines.append(citadel())
    for (name, class_id, flag, extra, site), (distance, angle) in zip(
        PLANETS, ORBITS, strict=True
    ):
        lines.append(spawn_planet(class_id, flag, distance, angle, extra))
        lines.append(finish_planet(flag, name, site))
    lines.append(spawn_rift())
    for type_id, distance, angle in RUINED_MEGAS:
        lines.append(spawn_ruined(type_id, distance, angle))
    lines.append(survey())
    return lines


def main() -> None:
    lines = build_lines()
    write_run("eventsystem.txt", lines)
    path = OUT / "eventsystem.txt"
    print(f"wrote {path} ({path.stat().st_size} bytes, {len(lines)} commands)")


if __name__ == "__main__":
    main()
