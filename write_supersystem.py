#!/usr/bin/env python3
"""Generate the Stellaris 4.x super-system run script.

Select the system's star, then: run supersystem.txt
The system stays unowned. Worlds stay uncolonized. No buildings, no starbase.
"""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent / "run_scripts"

PLAYER_ID = 0
RUNNER = "event_target:runner"
RUNNER_SPECIES = "event_target:runner_species"

# Clausewitz console truncates long run-lines. Pack below the hard cap.
MAX_CONSOLE_LINE = 1600
PACK_CONSOLE_LINE = 1400

PLANET_SIZE = 78
HABITAT_SIZE = 78

# Same unfinished sites as megasystem_all_compatible.txt, inner ring only.
UNFINISHED_MEGAS = (
    ("think_tank_0", 32, 0),
    ("spy_orb_0", 40, 40),
    ("strategic_coordination_center_0", 48, 80),
    ("mega_art_installation_0", 56, 120),
    ("interstellar_assembly_0", 64, 160),
    ("mega_shipyard_0", 72, 200),
    ("gateway_0", 84, 250),
)

# One of each vanilla planetary-extraction deposit (district caps / rare features).
EXTRACTION_DEPOSITS = (
    "d_arid_highlands",
    "d_hot_springs",
    "d_rushing_waterfalls",
    "d_searing_desert",
    "d_frozen_gas_lake",
    "d_geothermal_vent",
    "d_underwater_vent",
    "d_tempestous_mountain",
    "d_buzzing_plains",
    "d_veiny_cliffs",
    "d_mineral_fields",
    "d_prosperous_mesa",
    "d_ore_rich_caverns",
    "d_rich_mountain",
    "d_submerged_ore_veins",
    "d_mineral_striations",
    "d_betharian_deposit",
    "d_lichen_fields",
    "d_bountiful_plains",
    "d_rugged_woods",
    "d_green_hills",
    "d_forgiving_tundra",
    "d_boggy_fens",
    "d_nutritious_mudland",
    "d_fungal_caves",
    "d_lush_jungle",
    "d_fertile_lands",
    "d_great_river",
    "d_black_soil",
    "d_teeming_reef",
    "d_marvelous_oasis",
    "d_tropical_island",
    "d_fungal_forest",
    "d_natural_farmland",
    "d_dust_caverns",
    "d_dust_desert",
    "d_bubbling_swamp",
    "d_fuming_bog",
    "d_crystalline_caverns",
    "d_crystal_forest",
    "d_crystal_reef",
)

# Completed colony-event deposits that add districts. Not blockers.
EVENT_DISTRICT_DEPOSITS = (
    "d_underground_farm",
    "d_underground_mine",
    "d_underground_generator",
    "d_underground_contact_zone",
    "d_hyperfertile_valley",
    "d_ancient_mining_site",
    "d_harvester_fields",
    "d_migrating_forest_reserve",
    "d_junk_wastes",
    "d_junk_canals",
    "d_junk_hollows",
    "d_dayside_farm",
    "d_numas_breath",
    "d_worm_mine",
    "d_worm_farm",
    "d_abandoned_primitive_homesteads",
    "d_impact_crater",
    "d_metal_boneyard",
    "d_irradiated_valley",
    "d_organic_landfill",
)

# Useful positive planet modifiers. Each Gaia gets a unique mix.
USEFUL_MODIFIERS = (
    "lush_planet",
    "ultra_rich",
    "mineral_rich",
    "natural_beauty",
    "titanic_life",
    "abundant_geothermal_activity",
    "subterranean_wildlife",
    "rich_mircoflora",
    "atmospheric_hallucinogen_good",
    "atmospheric_aphrodisiac",
    "strong_magnetic_field",
    "high_gravity",
    "asteroid_belt",
    "hazardous_weather",
    "wild_storms",
    "subterranean_civilization",
    "subterranean_expansion",
    "gaia_world",
    "friendly_trees",
    "extensive_moon_system",
)


def player_scope() -> str:
    """Human player. Console owner = 0 is not a country scope and silently fails."""
    return (
        "random_playable_country = { limit = { is_ai = no } "
        "save_event_target_as = runner "
        "owner_main_species = { save_event_target_as = runner_species } }"
    )


def wrap_system(inner: str) -> str:
    return f"effect solar_system = {{ {inner} }}"


def with_player_system(inner: str) -> str:
    return "effect { " + player_scope() + " solar_system = { " + inner + " } }"


def planet_flag(name: str) -> str:
    return "ss_" + name.lower().removeprefix("ss ").replace(" ", "_")


def name_token(name: str) -> str:
    return name.replace(" ", "_").replace('"', "")


def planet_prefix(flag: str) -> str:
    return (
        "effect solar_system = { random_system_planet = { "
        f"limit = {{ has_planet_flag = {flag} }} "
    )


def planet_suffix() -> str:
    return " } }"


def split_planet_effects(flag: str, parts: list[str]) -> list[str]:
    """Several short planet-scoped effects instead of one truncated line."""
    prefix = planet_prefix(flag)
    suffix = planet_suffix()
    budget = PACK_CONSOLE_LINE - len(prefix) - len(suffix)
    if budget < 80:
        raise ValueError(f"prefix too long for {flag}")
    lines: list[str] = []
    chunk: list[str] = []
    size = 0
    for part in parts:
        extra = len(part) + (1 if chunk else 0)
        if chunk and size + extra > budget:
            lines.append(prefix + " ".join(chunk) + suffix)
            chunk = [part]
            size = len(part)
        else:
            if chunk:
                size += 1
            chunk.append(part)
            size += len(part)
    if chunk:
        lines.append(prefix + " ".join(chunk) + suffix)
    return lines


def spawn_planet_line(
    class_id: str,
    flag: str,
    distance: int,
    angle: int,
    size: int,
    extra_init: str = "",
) -> str:
    """Do not use console `own` here: with the star selected it colonizes the star."""
    more = f" {extra_init}" if extra_init else ""
    return wrap_system(
        f"spawn_planet = {{ class = {class_id} location = star orbit_location = yes "
        f"orbit_distance_offset = {distance} orbit_angle_offset = {angle} "
        f"size = {size} has_ring = no "
        f"init_effect = {{ set_planet_flag = {flag} set_planet_size = {size} "
        f"prevent_anomaly = yes{more} }} }}"
    )


def rename_flag_effect(flag: str, name: str) -> str:
    token = name_token(name)
    return wrap_system(
        "random_system_planet = { "
        f"limit = {{ has_planet_flag = {flag} }} set_name = {token} }}"
    )


def wipe_effects() -> list[str]:
    """Strip the selected system to a bare unowned star."""
    stations = wrap_system(
        "star = { if = { limit = { is_colony = yes } destroy_colony = yes } } "
        "if = { limit = { exists = starbase } starbase = { fleet = { delete_fleet = this } } } "
        "every_system_megastructure = { remove_megastructure = this } "
        "every_system_ambient_object = { destroy_ambient_object = this } "
        "every_fleet_in_system = { limit = { OR = { "
        "is_ship_class = shipclass_starbase "
        "is_ship_class = shipclass_mining_station "
        "is_ship_class = shipclass_research_station "
        "is_ship_class = shipclass_military_station } } "
        "delete_fleet = this }"
    )
    planets = wrap_system(
        "every_system_planet = { limit = { is_star = no } "
        "if = { limit = { exists = orbital_station } "
        "orbital_station = { delete_fleet = this } } "
        "if = { limit = { is_colony = yes } destroy_colony = yes } "
        "remove_planet = yes }"
    )
    return [stations, planets]


def spawn_mega_line(type_id: str, distance: int, angle: int) -> str:
    """Construction site for later repair. Owner is the human player, not the system."""
    return with_player_system(
        "spawn_megastructure = { "
        f"type = {type_id} planet = prev owner = {RUNNER} "
        f"orbit_distance = {distance} orbit_angle = {angle} "
        "}"
    )


def spawn_habitat_on_asteroid(asteroid_flag: str, hab_flag: str) -> str:
    """Habitat planet above the asteroid. No megastructure owner required."""
    return wrap_system(
        "random_system_planet = { "
        f"limit = {{ has_planet_flag = {asteroid_flag} }} "
        "spawn_planet = { class = pc_habitat location = this orbit_location = yes "
        "orbit_distance_offset = 8 orbit_angle_offset = 135 "
        f"size = {HABITAT_SIZE} has_ring = no "
        "init_effect = { "
        f"set_planet_flag = {hab_flag} set_planet_size = {HABITAT_SIZE} "
        "prevent_anomaly = yes set_planet_flag = habitat "
        "set_carrier_flag = habitat set_carrier_flag = megastructure "
        "} } }"
    )


def planet_orbits() -> list[tuple[int, int]]:
    """8 rings × 5. Starts past the mega ring (32–84) so worlds do not sit on sites."""
    orbits: list[tuple[int, int]] = []
    for ring, distance in enumerate((105, 130, 155, 180, 205, 230, 255, 280)):
        start = 36 if ring % 2 else 0
        for i in range(5):
            orbits.append((distance, (start + i * 72) % 360))
    return orbits


def asteroid_orbits() -> list[tuple[int, int]]:
    """Outer belt. Same 20-slot / 18° layout as before."""
    return [(308, (9 + i * 18) % 360) for i in range(20)]


def science_deposits() -> list[str]:
    return [
        "while = { count = 50 add_deposit = d_physics_10 }",
        "while = { count = 33 add_deposit = d_society_15 }",
        "add_deposit = d_society_5",
        "while = { count = 50 add_deposit = d_engineering_10 }",
        "while = { count = 50 add_deposit = d_dark_matter_deposit_10 }",
        "while = { count = 100 add_deposit = d_zro_deposit_5 }",
        "while = { count = 166 add_deposit = d_astral_threads_deposit_3 }",
        "add_deposit = d_astral_threads_deposit_1",
        "add_deposit = d_astral_threads_deposit_1",
        "while = { count = 166 add_deposit = d_artifacts_research_3 }",
        "add_deposit = d_artifacts_research_1",
        "add_deposit = d_artifacts_research_1",
        "while = { count = 500 add_deposit = d_nanites_deposit }",
        "while = { count = 167 add_deposit = d_vast_unity_deposit }",
    ]


def basic_deposits() -> list[str]:
    return [
        "while = { count = 50 add_deposit = d_energy_10 }",
        "while = { count = 50 add_deposit = d_minerals_10 }",
        "while = { count = 50 add_deposit = d_food_10 }",
        "while = { count = 20 add_deposit = d_alloys_25 }",
    ]


def other_mining_deposits() -> list[str]:
    return [
        "while = { count = 100 add_deposit = d_exotic_gases_5 }",
        "while = { count = 100 add_deposit = d_rare_crystals_5 }",
        "while = { count = 100 add_deposit = d_volatile_motes_5 }",
        "while = { count = 500 add_deposit = d_living_metal_deposit }",
        "while = { count = 50 add_deposit = d_trade_value_10 }",
        "while = { count = 166 add_deposit = d_artifacts_mining_3 }",
        "add_deposit = d_artifacts_mining_1",
        "add_deposit = d_artifacts_mining_1",
    ]


def gaia_modifier_set(index: int) -> tuple[str, ...]:
    """Five useful modifiers; each of the 20 Gaia worlds gets a different mix."""
    offsets = (0, 4, 8, 13, 17)
    return tuple(USEFUL_MODIFIERS[(index + offset) % len(USEFUL_MODIFIERS)] for offset in offsets)


def ecu_effects() -> list[str]:
    """78 housing + 78 of each urban type share one cap. Size 78 is only 78 total."""
    return [
        "clear_blockers = yes",
        "while = { count = 39 add_deposit = d_lithoid_crater }",
    ]


def gaia_effects(index: int) -> list[str]:
    parts = ["clear_blockers = yes"]
    parts.extend(f"add_modifier = {{ modifier = {mod} }}" for mod in gaia_modifier_set(index))
    parts.extend(f"add_deposit = {dep}" for dep in EXTRACTION_DEPOSITS)
    parts.extend(f"add_deposit = {dep}" for dep in EVENT_DISTRICT_DEPOSITS)
    # Pad rural caps to ~78 of each type after the unique/event stack.
    parts.append("while = { count = 13 add_deposit = d_geothermal_vent }")
    parts.append("while = { count = 8 add_deposit = d_ancient_mining_site }")
    parts.append("while = { count = 4 add_deposit = d_harvester_fields }")
    return parts


def write_run(name: str, body: str) -> None:
    lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    for i, stripped in enumerate(lines, start=1):
        if stripped.endswith("{") or stripped.endswith("="):
            raise ValueError(
                f"{name}:{i}: кожна команда має бути цілком в одному рядку, зламано: {stripped[:80]}"
            )
        if len(stripped) > MAX_CONSOLE_LINE:
            raise ValueError(
                f"{name}:{i}: рядок {len(stripped)} символів, консоль обріже "
                f"(ліміт {MAX_CONSOLE_LINE}): {stripped[:80]}"
            )
    (OUT / name).write_text("\n".join(lines), encoding="utf-8")


def build_lines() -> list[str]:
    lines: list[str] = []
    lines.extend(wipe_effects())

    orbits = planet_orbits()
    if len(orbits) != 40:
        raise ValueError(f"expected 40 planet orbits, got {len(orbits)}")

    ecu_slots = [orbits[i] for i in range(0, 40, 2)]
    gaia_slots = [orbits[i] for i in range(1, 40, 2)]
    if len(ecu_slots) != 20 or len(gaia_slots) != 20:
        raise ValueError("need 20 ecumenopolis and 20 Gaia slots")

    for i, (distance, angle) in enumerate(ecu_slots, start=1):
        name = f"SS Ecu {i}"
        flag = planet_flag(name)
        lines.append(spawn_planet_line("pc_city", flag, distance, angle, PLANET_SIZE))
        lines.append(rename_flag_effect(flag, name))
        lines.extend(split_planet_effects(flag, ecu_effects()))

    for i, (distance, angle) in enumerate(gaia_slots, start=1):
        name = f"SS Gaia {i}"
        flag = planet_flag(name)
        lines.append(spawn_planet_line("pc_gaia", flag, distance, angle, PLANET_SIZE))
        lines.append(rename_flag_effect(flag, name))
        lines.extend(split_planet_effects(flag, gaia_effects(i - 1)))

    ast = asteroid_orbits()
    asteroid_jobs: list[tuple[str, int, int, list[str]]] = []
    for i in range(5):
        distance, angle = ast[i]
        asteroid_jobs.append((f"SS Science {i + 1}", distance, angle, science_deposits()))
    for i in range(10):
        distance, angle = ast[5 + i]
        asteroid_jobs.append((f"SS Basics {i + 1}", distance, angle, basic_deposits()))
    for i in range(5):
        distance, angle = ast[15 + i]
        asteroid_jobs.append((f"SS Rares {i + 1}", distance, angle, other_mining_deposits()))

    for name, distance, angle, deposits in asteroid_jobs:
        flag = planet_flag(name)
        lines.append(spawn_planet_line("pc_asteroid", flag, distance, angle, 5))
        lines.append(rename_flag_effect(flag, name))
        lines.extend(split_planet_effects(flag, deposits))
        hab_name = name.replace("SS ", "SS Hab ", 1)
        hab_flag = planet_flag(hab_name)
        lines.append(spawn_habitat_on_asteroid(flag, hab_flag))
        lines.append(rename_flag_effect(hab_flag, hab_name))

    for type_id, distance, angle in UNFINISHED_MEGAS:
        lines.append(spawn_mega_line(type_id, distance, angle))
    return lines


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lines = build_lines()
    write_run("supersystem.txt", "\n".join(lines) + "\n")
    path = OUT / "supersystem.txt"
    print(f"wrote {path} ({path.stat().st_size} bytes, {len(lines)} commands)")


if __name__ == "__main__":
    main()
