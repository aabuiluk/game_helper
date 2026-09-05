#!/usr/bin/env python3
"""Generate Stellaris 4.x console run scripts into run_scripts/."""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent / "run_scripts"


def spawn_mega(type_id: str, distance: int, angle: int) -> str:
    return (
        "effect solar_system = { spawn_megastructure = { "
        f"type = {type_id} planet = prev owner = space_owner "
        f"orbit_distance = {distance} orbit_angle = {angle} "
        "} }"
    )


def spawn_on_body(type_id: str) -> str:
    return (
        "effect solar_system = { spawn_megastructure = { "
        f"type = {type_id} planet = prev owner = space_owner "
        "} }"
    )


def star_system_spawn(type_id: str, star_class: str | None = None) -> str:
    inner = f"set_star_class = {star_class} " if star_class else ""
    return (
        "effect solar_system = { "
        f"{inner}"
        "spawn_megastructure = { "
        f"type = {type_id} planet = prev owner = space_owner "
        "} }"
    )


def add_districts(district: str, count: int) -> str:
    return (
        f"effect while = {{ count = {count} add_district = {{ "
        f"district_type = {district} ignore_cap = yes }} }}\n"
    )


def add_zone(district: str, zone: str, slot: int = 1) -> str:
    return (
        "effect add_zone = { "
        f"district = {district} zone = {zone} zone_slot = {slot} replace = yes "
        "}\n"
    )


def add_buildings_simple(building: str, count: int) -> str:
    return f"effect while = {{ count = {count} add_building = {building} }}\n"


def add_buildings_zoned(district: str, zone: str, building: str, count: int) -> str:
    return (
        f"effect while = {{ count = {count} add_building = {{ "
        f"district = {district} zone = {zone} building = {building} }} }}\n"
    )


def amenities_crime() -> str:
    return (
        add_buildings_simple("building_paradise_dome", 2)
        + add_buildings_simple("building_holo_theatres", 3)
        + add_buildings_simple("building_luxury_residence", 2)
        + add_buildings_simple("building_precinct_house", 2)
        + add_buildings_simple("building_medical_3", 1)
    )


def spawn_ring() -> str:
    return spawn_on_body("orbital_ring_restored") + "\n"


ECU_ZONES = {
    "district_arcology_housing": "zone_unity_arcology",
    "district_arcology_leisure": "zone_unity_arcology",
    "district_arcology_arms_industry": "zone_foundry_arcology",
    "district_arcology_civilian_industry": "zone_factory_arcology",
    "district_arcology_research": "zone_research_arcology",
    "district_arcology_research_physics": "zone_research_physics_arcology",
    "district_arcology_research_society": "zone_research_society_arcology",
    "district_arcology_research_engineering": "zone_research_engineering_arcology",
    "district_arcology_administrative": "zone_unity_arcology",
    "district_arcology_trade": "zone_trade_arcology",
    "district_arcology_fortress": "zone_fortress_arcology",
}

OLD_DISTRICTS = (
    "district_city",
    "district_farming",
    "district_generator",
    "district_mining",
    "district_industrial",
    "district_arcology_urban_1",
    "district_arcology_urban_2",
    "district_arcology_urban_3",
)


def _while_district(district: str, count: int) -> str:
    return (
        f"while = {{ count = {count} add_district = {{ "
        f"district_type = {district} ignore_cap = yes }} }}"
    )


def _while_building(building: str, count: int) -> str:
    return f"while = {{ count = {count} add_building = {building} }}"


def _while_building_zoned(district: str, zone: str, building: str, count: int) -> str:
    return (
        f"while = {{ count = {count} add_building = {{ "
        f"district = {district} zone = {zone} building = {building} }} }}"
    )


def _fill_zones(districts: list[tuple[str, int]]) -> list[str]:
    parts: list[str] = []
    index = 0
    for district, count in districts:
        zone = ECU_ZONES.get(district, "zone_unity_arcology")
        for _ in range(count):
            parts.append(
                f"add_zone = {{ district = {index} zone = {zone} zone_slot = 1 replace = yes }}"
            )
            parts.append(
                f"add_zone = {{ district = {index} zone = {zone} zone_slot = 2 replace = yes }}"
            )
            index += 1
    return parts


def ecu_planet(
    districts: list[tuple[str, int]],
    zones: list[tuple[str, str]],
    zoned_buildings: list[tuple[str, str, str, int]],
    buildings: list[tuple[str, int]],
    pops: int,
) -> str:
    parts = [
        "clear_blockers = yes",
        "remove_building = building_colony_shelter",
        "remove_building = building_capital",
        "remove_building = building_major_capital",
        "remove_building = building_imperial_capital",
        "add_building = building_system_capital",
    ]
    parts.extend(f"while = {{ count = 80 remove_district = {old} }}" for old in OLD_DISTRICTS)
    parts.extend(_while_district(district, count) for district, count in districts)
    parts.extend(_fill_zones(districts))
    parts.extend(
        f"add_zone = {{ district = {district} zone = {zone} zone_slot = 1 replace = yes }}"
        for district, zone in zones
    )
    parts.extend(
        _while_building_zoned(district, zone, building, count)
        for district, zone, building, count in zoned_buildings
    )
    buildings = [(b, c) for b, c in buildings if b != "building_imperial_capital"]
    parts.extend(_while_building(building, count) for building, count in buildings)
    parts.append(
        "solar_system = { spawn_megastructure = { "
        "type = orbital_ring_restored planet = prev owner = space_owner } }"
    )
    return (
        "planet_class pc_city\n"
        "planet_size 78\n"
        "effect { " + " ".join(parts) + " }\n"
        f"add_pops 0 {pops}\n"
    )


PACK_CONSOLE_LINE = 1400

# Rural + slot + output bonuses that actually help a Gaia 78.
GAIA_MODIFIERS = (
    "gaia_world",
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
    "friendly_trees",
    "eat_the_titans",
    "mastery_of_nature",
    "cultivated_worldscaping_modifier",
    "wooden_planet",
    "volcanic_oasis",
    "infernal_library",
    "volcanic_ultra_rich",
    "volcanic_subterranean",
    "remnants_of_court_of_blossoms",
    "happy_anathari",
)

# City-world: jobs %, happiness, housing, extra total slots. Skip rural-only / happiness penalties.
ECU_MODIFIERS = (
    "gaia_world",
    "natural_beauty",
    "atmospheric_hallucinogen_good",
    "atmospheric_aphrodisiac",
    "titanic_life",
    "friendly_trees",
    "remnants_of_court_of_blossoms",
    "happy_anathari",
    "infernal_library",
    "wooden_planet",
    "volcanic_oasis",
    "mastery_of_nature",
    "cultivated_worldscaping_modifier",
    "subterranean_expansion",
    "high_gravity",
    "lush_planet",
    "low_gravity",
    "wasteland_infrastructure",
    "pyroglyphic_codex_mod",
)

DISTRICT_COUNT = 70

ECU_DISTRICTS = (
    "district_arcology_housing",
    "district_arcology_urban_1",
    "district_arcology_urban_2",
    "district_arcology_urban_3",
)


def _pack_effect(parts: list[str]) -> list[str]:
    prefix = "effect { "
    suffix = " }"
    budget = PACK_CONSOLE_LINE - len(prefix) - len(suffix)
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


def _deposit_counts(items: tuple[tuple[str, int], ...]) -> list[str]:
    lines: list[str] = []
    for deposit_id, count in items:
        if count <= 0:
            continue
        if count == 1:
            lines.append(f"add_deposit = {deposit_id}")
        else:
            lines.append(f"while = {{ count = {count} add_deposit = {deposit_id} }}")
    return lines


# Overlay «Родовище / фіча»: only +generator / +mining / +farming. 3 of each.
# No underground / betharian / rares / orbital. Same ID may not stack in 4.x.
GAIA_FEATURE_DEPOSITS = (
    "d_hot_springs",
    "d_arid_highlands",
    "d_buzzing_plains",
    "d_rushing_waterfalls",
    "d_searing_desert",
    "d_frozen_gas_lake",
    "d_geothermal_vent",
    "d_underwater_vent",
    "d_tempestous_mountain",
    "d_veiny_cliffs",
    "d_mineral_fields",
    "d_prosperous_mesa",
    "d_ore_rich_caverns",
    "d_rich_mountain",
    "d_submerged_ore_veins",
    "d_ancient_mining_site",
    "d_lichen_fields",
    "d_bountiful_plains",
    "d_rugged_woods",
    "d_green_hills",
    "d_forgiving_tundra",
    "d_boggy_fens",
    "d_nutritious_mudland",
    "d_natural_farmland",
    "d_fungal_caves",
    "d_lush_jungle",
    "d_fertile_lands",
    "d_great_river",
    "d_black_soil",
    "d_teeming_reef",
    "d_marvelous_oasis",
    "d_tropical_island",
    "d_fungal_forest",
    "d_hyperfertile_valley",
    "d_harvester_fields",
)
GAIA_DEPOSITS = tuple((deposit_id, 3) for deposit_id in GAIA_FEATURE_DEPOSITS)

# No lithoid_crater: potential is origin_lithoid and aborts the rest of the effect.
ECU_DEPOSITS = (
    ("d_underground_generator", 1),
    ("d_underground_mine", 1),
    ("d_underground_farm", 1),
    ("d_numas_breath", 1),
    ("d_underground_contact_zone", 1),
    ("d_betharian_deposit", 1),
    ("d_alien_pets_deposit", 1),
)

ECU_STRIP = (
    "district_arcology_housing",
    "district_arcology_leisure",
    "district_arcology_arms_industry",
    "district_arcology_civilian_industry",
    "district_arcology_research",
    "district_arcology_research_physics",
    "district_arcology_research_society",
    "district_arcology_research_engineering",
    "district_arcology_administrative",
    "district_arcology_trade",
    "district_arcology_fortress",
)


def _bare_world(
    class_id: str,
    districts: tuple[str, ...],
    modifiers: tuple[str, ...],
    deposits: tuple[tuple[str, int], ...],
) -> str:
    """Size 78 base, no buildings, no pops. Then pad slots and add 70 of each district."""
    extra = ECU_STRIP if class_id == "pc_city" else ()
    setup = [
        "clear_blockers = yes",
        *[f"while = {{ count = 120 remove_district = {old} }}" for old in OLD_DISTRICTS],
        *[f"while = {{ count = 120 remove_district = {dist} }}" for dist in extra],
    ]
    modifier_parts = [f"add_modifier = {{ modifier = {mod} }}" for mod in modifiers]
    lines = [
        f"planet_class {class_id}",
        "planet_size 78",
        *_pack_effect(setup + modifier_parts),
        *_pack_effect(_deposit_counts(deposits)),
    ]
    for district in districts:
        lines.append(f"effect {{ {_while_district(district, DISTRICT_COUNT)} }}")
    lines.append("planet_size 78")
    return "\n".join(lines) + "\n"


def gaia_planet() -> str:
    """Gaia 78: overlay feature deposits ×3 each. No forced districts, no special deposits."""
    setup = [
        "clear_blockers = yes",
        *[f"while = {{ count = 120 remove_district = {old} }}" for old in OLD_DISTRICTS],
        *[f"while = {{ count = 120 remove_district = {dist} }}" for dist in ECU_STRIP],
    ]
    modifier_parts = [f"add_modifier = {{ modifier = {mod} }}" for mod in GAIA_MODIFIERS]
    lines = [
        "planet_class pc_gaia",
        "planet_size 78",
        *_pack_effect(setup + modifier_parts),
        *[f"effect {{ {part} }}" for part in _deposit_counts(GAIA_DEPOSITS)],
    ]
    return "\n".join(lines) + "\n"


def ecu_bare_planet() -> str:
    return _bare_world("pc_city", ECU_DISTRICTS, ECU_MODIFIERS, ECU_DEPOSITS)


def ring_modules(modules: list[str], buildings: list[str]) -> str:
    lines: list[str] = []
    for i, module in enumerate(modules, start=1):
        lines.append(f"effect set_starbase_module = {{ slot = {i} module = {module} }}")
    for i, building in enumerate(buildings, start=1):
        lines.append(f"effect set_starbase_building = {{ slot = {i} building = {building} }}")
    return "\n".join(lines) + "\n"


def repeat_lines(body: str, times: int = 10) -> str:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    return "\n".join(lines * times) + "\n"


def write(name: str, body: str) -> None:
    if name == "README.txt":
        (OUT / name).write_text(body.rstrip() + "\n", encoding="utf-8")
        return
    lines = [line.strip() for line in body.splitlines() if line.strip() and not line.strip().startswith("#")]
    for i, stripped in enumerate(lines, start=1):
        if stripped.endswith("{") or stripped.endswith("="):
            raise ValueError(
                f"{name}: console run виконує КОЖЕН рядок окремо. "
                f"Команда має бути цілком в одному рядку, зламано: {stripped}"
            )
        if name in {"gaia78_capital_planet.txt", "ecu78_capital_planet.txt"} and len(stripped) > 1600:
            raise ValueError(
                f"{name}:{i}: рядок {len(stripped)} символів, консоль обріже (ліміт 1600)"
            )
    # Без порожнього рядка в кінці: run трактує його як Unknown command.
    (OUT / name).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    write(
        "megasystem_all_compatible.txt",
        "\n".join(
            [
                spawn_mega("think_tank_0", 32, 0),
                spawn_mega("spy_orb_0", 40, 40),
                spawn_mega("strategic_coordination_center_0", 48, 80),
                spawn_mega("mega_art_installation_0", 56, 120),
                spawn_mega("interstellar_assembly_0", 64, 160),
                spawn_mega("mega_shipyard_0", 72, 200),
                spawn_mega("gateway_0", 84, 250),
            ]
        )
        + "\n",
    )

    write("system_dyson.txt", star_system_spawn("dyson_sphere_0", "sc_g") + "\n")
    write("system_dyson_swarm.txt", star_system_spawn("dyson_swarm_1") + "\n")
    write(
        "system_ringworld.txt",
        "effect solar_system = { set_star_class = sc_g "
        "spawn_megastructure = { type = ring_world_1 planet = prev owner = space_owner orbit_distance = 45 orbit_angle = 0 } }\n",
    )
    write("system_matter_decompressor.txt", star_system_spawn("matter_decompressor_0", "sc_black_hole") + "\n")
    write("system_quantum_catapult.txt", star_system_spawn("quantum_catapult_0", "sc_pulsar") + "\n")
    write("system_stellar_cannon.txt", star_system_spawn("dyson_gun_0") + "\n")
    write("system_arc_furnace.txt", spawn_on_body("orbital_arc_furnace_1") + "\n")

    # --- Ecumenopolis planets ---
    amenities = [
        ("building_paradise_dome", 2),
        ("building_holo_theatres", 3),
        ("building_luxury_residence", 2),
        ("building_precinct_house", 2),
        ("building_medical_3", 1),
    ]

    write("ecu78_capital_planet.txt", ecu_bare_planet())
    write("gaia78_capital_planet.txt", gaia_planet())

    write(
        "ecu78_alloys_planet.txt",
        ecu_planet(
            [
                ("district_arcology_housing", 22),
                ("district_arcology_leisure", 6),
                ("district_arcology_arms_industry", 50),
            ],
            [("district_arcology_arms_industry", "zone_foundry_arcology")],
            [("district_arcology_arms_industry", "zone_foundry_arcology", "building_foundry_3", 6)],
            [("building_ministry_production", 1), ("building_foundry_efficiency_1", 1), *amenities],
            38000,
        ),
    )

    write(
        "ecu78_consumer_goods_planet.txt",
        ecu_planet(
            [
                ("district_arcology_housing", 22),
                ("district_arcology_leisure", 6),
                ("district_arcology_civilian_industry", 50),
            ],
            [("district_arcology_civilian_industry", "zone_factory_arcology")],
            [("district_arcology_civilian_industry", "zone_factory_arcology", "building_factory_3", 6)],
            [("building_ministry_production", 1), ("building_factory_efficiency_1", 1), *amenities],
            38000,
        ),
    )

    write(
        "ecu78_unity_planet.txt",
        ecu_planet(
            [
                ("district_arcology_housing", 20),
                ("district_arcology_leisure", 10),
                ("district_arcology_administrative", 48),
            ],
            [("district_arcology_administrative", "zone_unity_arcology")],
            [("district_arcology_administrative", "zone_unity_arcology", "building_bureaucratic_3", 6)],
            [("building_autochthon_monument", 1), *amenities],
            36000,
        ),
    )

    write(
        "ecu78_research_planet.txt",
        ecu_planet(
            [
                ("district_arcology_housing", 18),
                ("district_arcology_leisure", 6),
                ("district_arcology_research", 28),
                ("district_arcology_research_physics", 9),
                ("district_arcology_research_society", 8),
                ("district_arcology_research_engineering", 9),
            ],
            [("district_arcology_research", "zone_research_arcology")],
            [("district_arcology_research", "zone_research_arcology", "building_research_lab_3", 6)],
            [("building_institute", 1), ("building_supercomputer", 1), *amenities],
            40000,
        ),
    )

    write(
        "ecu78_trade_planet.txt",
        ecu_planet(
            [
                ("district_arcology_housing", 20),
                ("district_arcology_leisure", 6),
                ("district_arcology_trade", 52),
            ],
            [("district_arcology_trade", "zone_trade_arcology")],
            [("district_arcology_trade", "zone_trade_arcology", "building_commercial_megaplex", 4)],
            [("building_galactic_stock_exchange", 1), ("building_commercial_forum", 1), *amenities],
            36000,
        ),
    )

    write(
        "ecu78_fortress_planet.txt",
        ecu_planet(
            [
                ("district_arcology_housing", 18),
                ("district_arcology_leisure", 4),
                ("district_arcology_fortress", 56),
            ],
            [("district_arcology_fortress", "zone_fortress_arcology")],
            [],
            [
                ("building_fortress", 4),
                ("building_stronghold", 2),
                ("building_military_academy", 1),
                ("building_planetary_shield_generator", 1),
                *amenities,
            ],
            40000,
        ),
    )

    write(
        "ecu78_capital_ring.txt",
        ring_modules(
            [
                "orbital_ring_habitation",
                "orbital_ring_shipyard",
                "orbital_ring_anchorage",
                "orbital_ring_gun_battery",
            ],
            [
                "orbitalring_alloy_hub",
                "orbitalring_bureaucracy_hub",
                "orbitalring_embassy_complex",
            ],
        ),
    )
    write(
        "ecu78_alloys_ring.txt",
        ring_modules(
            [
                "orbital_ring_habitation",
                "orbital_ring_shipyard",
                "orbital_ring_anchorage",
                "orbital_ring_gun_battery",
            ],
            [
                "orbitalring_alloy_hub",
                "orbitalring_mineral_hub",
                "orbitalring_maintenance_hub",
            ],
        ),
    )
    write(
        "ecu78_consumer_goods_ring.txt",
        ring_modules(
            [
                "orbital_ring_habitation",
                "orbital_ring_anchorage",
                "orbital_ring_hangar_bay",
                "orbital_ring_gun_battery",
            ],
            [
                "orbitalring_consumer_hub",
                "orbitalring_trade_hub",
                "orbitalring_galactic_stock_exchange",
            ],
        ),
    )
    write(
        "ecu78_unity_ring.txt",
        ring_modules(
            [
                "orbital_ring_habitation",
                "orbital_ring_anchorage",
                "orbital_ring_gun_battery",
                "orbital_ring_hangar_bay",
            ],
            [
                "orbitalring_bureaucracy_hub",
                "orbitalring_embassy_complex",
                "orbitalring_maintenance_hub",
            ],
        ),
    )
    write(
        "ecu78_research_ring.txt",
        ring_modules(
            [
                "orbital_ring_habitation",
                "orbital_ring_gun_battery",
                "orbital_ring_hangar_bay",
                "orbital_ring_anchorage",
            ],
            [
                "orbitalring_energy_hub",
                "orbitalring_shield_generator",
                "orbitalring_maintenance_hub",
            ],
        ),
    )
    write(
        "ecu78_trade_ring.txt",
        ring_modules(
            [
                "orbital_ring_habitation",
                "orbital_ring_anchorage",
                "orbital_ring_hangar_bay",
                "orbital_ring_gun_battery",
            ],
            [
                "orbitalring_trade_hub",
                "orbitalring_galactic_stock_exchange",
                "orbitalring_consumer_hub",
            ],
        ),
    )
    write(
        "ecu78_fortress_ring.txt",
        ring_modules(
            [
                "orbital_ring_gun_battery",
                "orbital_ring_missile_battery",
                "orbital_ring_hangar_bay",
                "orbital_ring_anchorage",
            ],
            [
                "orbitalring_shield_generator",
                "orbitalring_maintenance_hub",
                "orbitalring_alloy_hub",
            ],
        ),
    )

    def ring_section(
        name: str,
        districts: list[tuple[str, int]],
        zones: list[tuple[str, str]],
        buildings: list[tuple[str, int]],
        pops: int,
    ) -> None:
        body = (
            "effect { remove_building = building_colony_shelter "
            "remove_building = building_capital remove_building = building_major_capital "
            "add_building = building_system_capital }\n"
        )
        for district, count in districts:
            body += add_districts(district, count)
        for district, zone in zones:
            body += add_zone(district, zone)
        for building, count in buildings:
            body += add_buildings_simple(building, count)
        body += amenities_crime()
        body += f"add_pops 0 {pops}\n"
        write(name, body)

    ring_section(
        "ring_research.txt",
        [("district_rw_city", 2), ("district_rw_science", 8)],
        [("district_rw_science", "zone_research_ring_world")],
        [("building_research_lab_3", 4), ("building_institute", 1), ("building_supercomputer", 1)],
        8000,
    )
    ring_section(
        "ring_trade.txt",
        [("district_rw_city", 2), ("district_rw_commercial", 8)],
        [("district_rw_commercial", "zone_trade_ring_world")],
        [("building_commercial_megaplex", 3), ("building_galactic_stock_exchange", 1)],
        8000,
    )
    ring_section(
        "ring_food.txt",
        [("district_rw_city", 2), ("district_rw_farming", 8)],
        [("district_rw_farming", "zone_food_ring_world")],
        [("building_hydroponics_farm", 4)],
        8000,
    )
    ring_section(
        "ring_unity.txt",
        [("district_rw_city", 10)],
        [("district_rw_city", "zone_unity_ring_world")],
        [("building_bureaucratic_3", 4), ("building_autochthon_monument", 1)],
        7000,
    )
    ring_section(
        "ring_general.txt",
        [
            ("district_rw_city", 3),
            ("district_rw_industrial", 2),
            ("district_rw_science", 2),
            ("district_rw_farming", 2),
            ("district_rw_commercial", 1),
        ],
        [
            ("district_rw_industrial", "zone_industrial_ring_world"),
            ("district_rw_science", "zone_research_ring_world"),
        ],
        [
            ("building_foundry_3", 1),
            ("building_factory_3", 1),
            ("building_research_lab_3", 1),
            ("building_bureaucratic_3", 1),
        ],
        8000,
    )
    ring_section(
        "ring_alloys.txt",
        [("district_rw_city", 2), ("district_rw_industrial", 8)],
        [("district_rw_industrial", "zone_foundry_ring_world")],
        [("building_foundry_3", 4), ("building_ministry_production", 1)],
        8000,
    )
    ring_section(
        "ring_energy.txt",
        [("district_rw_city", 2), ("district_rw_generator", 8)],
        [("district_rw_generator", "zone_energy_ring_world")],
        [("building_energy_nexus", 2)],
        8000,
    )

    orbital_resources_300 = (
        "effect while = { count = 30 add_deposit = d_energy_10 }\n"
        "effect while = { count = 30 add_deposit = d_minerals_10 }\n"
        "effect while = { count = 12 add_deposit = d_alloys_25 }\n"
        "effect while = { count = 30 add_deposit = d_food_10 }\n"
        "effect while = { count = 150 add_deposit = d_consumer_goods_obsessional_directive }\n"
    )
    write("orbital_resources_300.txt", orbital_resources_300)
    write("orbital_resources_3000.txt", repeat_lines(orbital_resources_300))

    orbital_energy_10000 = "\n".join(
        "effect while = { count = 100 add_deposit = d_energy_10 }"
        for _ in range(10)
    ) + "\n"
    write("orbital_energy_10000.txt", orbital_energy_10000)
    write("orbital_energy_100000.txt", repeat_lines(orbital_energy_10000))

    orbital_science_500 = (
        "effect while = { count = 50 add_deposit = d_physics_10 }\n"
        "effect while = { count = 33 add_deposit = d_society_15 }\n"
        "effect add_deposit = d_society_5\n"
        "effect while = { count = 50 add_deposit = d_engineering_10 }\n"
    )
    write("orbital_science_500.txt", orbital_science_500)
    write("orbital_science_5000.txt", repeat_lines(orbital_science_500))

    orbital_special_mining_100 = (
        "effect while = { count = 20 add_deposit = d_exotic_gases_5 }\n"
        "effect while = { count = 20 add_deposit = d_rare_crystals_5 }\n"
        "effect while = { count = 20 add_deposit = d_volatile_motes_5 }\n"
        "effect while = { count = 10 add_deposit = d_trade_value_10 }\n"
        "effect while = { count = 33 add_deposit = d_artifacts_mining_3 }\n"
        "effect add_deposit = d_artifacts_mining_1\n"
        "effect while = { count = 100 add_deposit = d_living_metal_deposit }\n"
    )
    write("orbital_special_mining_100.txt", orbital_special_mining_100)
    write("orbital_special_mining_1000.txt", repeat_lines(orbital_special_mining_100))

    write("orbital_special_resources_100.txt", "\n")

    orbital_special_research_100 = (
        "effect while = { count = 10 add_deposit = d_dark_matter_deposit_10 }\n"
        "effect while = { count = 20 add_deposit = d_zro_deposit_5 }\n"
        "effect while = { count = 33 add_deposit = d_astral_threads_deposit_3 }\n"
        "effect add_deposit = d_astral_threads_deposit_1\n"
        "effect while = { count = 33 add_deposit = d_artifacts_research_3 }\n"
        "effect add_deposit = d_artifacts_research_1\n"
        "effect while = { count = 100 add_deposit = d_nanites_deposit }\n"
        "effect while = { count = 100 add_deposit = d_vast_unity_deposit }\n"
    )
    write("orbital_special_research_100.txt", orbital_special_research_100)
    write("orbital_special_research_1000.txt", repeat_lines(orbital_special_research_100))

    write(
        "habitat_system_setup.txt",
        "effect solar_system = { every_system_planet = { limit = { is_star = no is_colony = no } "
        "add_deposit = d_minerals_10 add_deposit = d_minerals_10 add_deposit = d_minerals_10 "
        "add_deposit = d_energy_10 add_deposit = d_energy_10 add_deposit = d_energy_10 } }\n",
    )
    write("habitat_spawn_central.txt", spawn_on_body("habitat_central_complex") + "\n")
    write("habitat_spawn_major.txt", spawn_on_body("habitat_major_orbital") + "\n")
    write("habitat_spawn_minor.txt", spawn_on_body("habitat_minor_orbital") + "\n")

    def habitat(name: str, districts: list[tuple[str, int]], zones: list[tuple[str, str]], buildings: list[tuple[str, int]], pops: int) -> None:
        body = (
            "effect { remove_building = building_hab_capital "
            "remove_building = building_hab_major_capital "
            "add_building = building_hab_system_capital clear_blockers = yes }\n"
        )
        for district, count in districts:
            body += (
                f"effect while = {{ count = {count} add_district = {{ "
                f"district_type = {district} ignore_cap = yes }} }}\n"
            )
        for district, zone in zones:
            body += add_zone(district, zone)
        for building, count in buildings:
            body += add_buildings_simple(building, count)
        body += amenities_crime()
        body += f"add_pops 0 {pops}\n"
        write(name, body)

    habitat(
        "habitat_research.txt",
        [("district_hab_housing", 4), ("district_hab_cultural", 2), ("district_hab_science", 12)],
        [("district_hab_science", "zone_habitat_research")],
        [("building_research_lab_3", 4), ("building_institute", 1)],
        12000,
    )
    habitat(
        "habitat_trade.txt",
        [("district_hab_housing", 4), ("district_hab_cultural", 2), ("district_hab_commercial", 12)],
        [("district_hab_commercial", "zone_trade")],
        [("building_commercial_megaplex", 3), ("building_galactic_stock_exchange", 1)],
        11000,
    )
    habitat(
        "habitat_industry.txt",
        [("district_hab_housing", 4), ("district_hab_cultural", 2), ("district_hab_industrial", 12)],
        [("district_hab_industrial", "zone_foundry")],
        [("building_foundry_3", 3), ("building_factory_3", 2), ("building_ministry_production", 1)],
        12000,
    )
    habitat(
        "habitat_fortress.txt",
        [("district_hab_housing", 10), ("district_hab_cultural", 2), ("district_hab_industrial", 6)],
        [],
        [
            ("building_fortress", 4),
            ("building_stronghold", 2),
            ("building_military_academy", 1),
            ("building_planetary_shield_generator", 1),
        ],
        10000,
    )
    habitat(
        "habitat_mining.txt",
        [("district_hab_housing", 4), ("district_hab_cultural", 2), ("district_hab_mining", 12)],
        [],
        [("building_mining_districts_4", 2)],
        11000,
    )
    habitat(
        "habitat_energy.txt",
        [("district_hab_housing", 4), ("district_hab_cultural", 2), ("district_hab_energy", 12)],
        [("district_hab_energy", "zone_energy")],
        [("building_energy_nexus", 2)],
        11000,
    )

    write("README.txt", README)
    print(f"Wrote scripts to {OUT}")


README = r"""Stellaris 4.x run-скрипти (серпень 2026)
========================================

Куди класти файли
-----------------
Скопіюй усі .txt у:

  Documents/Paradox Interactive/Stellaris/

Саме звідти консоль бере `run filename.txt`.
Віджет читів має пункт меню «Встановити у папку Stellaris».

Як запускати
------------
ВАЖЛИВО: консоль Stellaris читає run-файл ПО РЯДКАХ як окремі команди.
Кожен `effect` має бути ЦІЛКОМ в одному рядку. Багаторядкові { } ламають файл.

1. Зніми Ironman (цей helper це вміє).
2. Відкрий консоль (` або Shift+Alt+C).
3. Виділи мишею потрібний об'єкт (див. таблицю).
4. Введи: run filename.txt
5. Система має бути твоя (зоряна база). Інакше owner = space_owner не спрацює.

add_pops 0 N бере вид з індексом 0 (зазвичай твій головний). Якщо попи не ті —
увімкни debugtooltip і підстав правильний species id.

Повторний запуск
----------------
Майже жоден файл не ідемпотентний: мегасооруження задублюються, райони
доб'ються до капу і зупиняться, попи додадуться ще раз. Запускай один раз.

Таблиця файлів
--------------
Файл | Що створює | Що виділити
supersystem.txt | 20 планет 78 + 20 астероїдів + цитадель + недобудовані мега | зірка (НЕ столиця)
eventsystem.txt | сусідня система: 16 незаселених 78 + археологія + rift + ruined меги | зірка суперсистеми
megasystem_all_compatible.txt | Майданчики Nexus/Sentry/SCC/Art/Assembly/Shipyard/Gateway (_0) | центральна зірка
system_dyson.txt | майданчик Dyson Sphere (dyson_sphere_0), зірка → sc_g | зірка
system_dyson_swarm.txt | перша стадія Dyson Swarm (dyson_swarm_1) | зірка
system_ringworld.txt | майданчик Ring World (ring_world_1), зірка → sc_g | зірка
system_matter_decompressor.txt | зірка → чорна діра + майданчик MD (_0) | зірка
system_quantum_catapult.txt | зірка → пульсар + майданчик Catapult (_0) | зірка
system_stellar_cannon.txt | майданчик Stellar Cannon (dyson_gun_0) | зірка
system_arc_furnace.txt | перша стадія Arc Furnace (_1) | molten-планета
ecu78_*_planet.txt | Ecumenopolis 78 + спавн Orbital Ring | колонія
ecu78_*_ring.txt | модулі/будівлі кільця | саме Orbital Ring
ring_*.txt | забудова секції Ring World | колонізована секція
orbital_resources_300.txt | energy/minerals/alloys/food/consumer goods ×300 | неживе тіло
orbital_resources_3000.txt | те саме ×3000 (10×300) | неживе тіло
orbital_energy_10000.txt | energy ×10000 (10×100 d_energy_10) | неживе тіло
orbital_energy_100000.txt | energy ×100000 (10×10000) | неживе тіло
orbital_science_500.txt | physics/society/engineering ×500 | неживе тіло
orbital_science_5000.txt | physics/society/engineering ×5000 | неживе тіло
orbital_special_resources_100.txt | не запускати (розділення mining/research) | —
orbital_special_mining_100.txt | стратегічні mining ×100 | неживе тіло
orbital_special_mining_1000.txt | стратегічні mining ×1000 | неживе тіло
orbital_special_research_100.txt | стратегічні research ×100 | неживе тіло
orbital_special_research_1000.txt | стратегічні research ×1000 | неживе тіло
habitat_system_setup.txt | депозити для district cap | зірка
habitat_spawn_*.txt | Central / Major / Minor Orbital | нежиле тіло
habitat_*.txt | забудова хабітата | колонізований хабітат

Мегасооруження | Можна в universal | Чому | Вимоги | Конфлікти
Усі пункти меню Мегасистеми спавнять НЕДОБУДОВАНИЙ майданчик (_0 / перша стадія), не готову споруду.
Science Nexus (think_tank_0) | так | орбітальний майданчик | система твоя | немає з іншими станціями
Sentry Array (spy_orb_0) | так | орбітальний майданчик | система твоя | немає
SCC (strategic_coordination_center_0) | так | орбітальний майданчик | система твоя | немає
Mega Art (mega_art_installation_0) | так | орбітальний майданчик | система твоя | немає
Interstellar Assembly (interstellar_assembly_0) | так | орбітальний майданчик | система твоя | немає
Mega Shipyard (mega_shipyard_0) | так | орбітальний майданчик | система твоя | немає
Gateway (gateway_0) | так | майданчик брами | система твоя | 1 брама на систему
Hyper Relay | — | немає стадії _0, лише готовий hyper_relay; у пакет не входить | — | —
Dyson Sphere (dyson_sphere_0) | ні | майданчик навколо зірки | звичайна зірка | Swarm, Cannon, Catapult, Ring World, MD
Dyson Swarm (dyson_swarm_1) | ні | перша стадія навколо зірки | звичайна зірка | Sphere / Cannon / Catapult
Ring World (ring_world_1) | ні | один майданчик, не 4 секції | звичайна зірка | Dyson, внутрішні планети
Matter Decompressor (matter_decompressor_0) | ні | майданчик на чорній дірі | sc_black_hole | не Dyson/Ring на тій зірці
Quantum Catapult (quantum_catapult_0) | ні | майданчик навколо зірки | пульсар/нейтрон/магнетар | Dyson/Swarm/Cannon
Stellar Cannon (dyson_gun_0) | ні | майданчик навколо зірки | звичайна зірка | Dyson/Swarm/Catapult
Arc Furnace (orbital_arc_furnace_1) | ні (інший scope) | перша стадія на molten | pc_molten | немає зі станціями; не зірка
Habitat / Orbital Ring | ні | тримаються за планету | планета | окремі файли
Aetherophasic Engine / Horizon Needle / Behemoth | ні | криза / кінець гри | — | навмисно не спавнимо
Grand Archive / Deep Space Citadel | ні | підтверджений лише site-ID (_0), не «готовий» | — | не вигадуємо complete-ID
think_tank_4 (Groik Nexus) | ні | іменований/особливий варіант, не стандартна добудова | — | використовуємо think_tank_0

Екуменополіс 78
---------------
Послідовність для кожної спеціалізації:
1. Виділи колонію. run ecu78_<spec>_planet.txt
2. Клацни нове Orbital Ring. run ecu78_<spec>_ring.txt

Райони (сума 78):
capital: 20 housing + 8 leisure + 12 foundry + 10 factory + 12 research + 10 admin + 6 trade
alloys: 22 housing + 6 leisure + 50 foundry
CG: 22 housing + 6 leisure + 50 factory
unity: 20 housing + 10 leisure + 48 admin
research: 18 housing + 6 leisure + 28 research + 9 physics + 8 society + 9 engineering
trade: 20 housing + 6 leisure + 52 trade
fortress: 18 housing + 4 leisure + 56 fortress

Попи (4.x workforce, не «старі» pops):
capital 34000, alloys/CG 38000, unity/trade 36000, research/fortress 40000.
Це під робочі місця районів + кілька будівель, з запасом житла.
Природні planetary features (джунглі, жили руди) не додаємо — для city-world це сміття.
building_system_capital може не стати, якщо столиця вже є — це нормально.

Orbital Ring: spawn у planet-файлі (scope планети). Модулі — окремий файл,
бо set_starbase_module / set_starbase_building вимагають scope starbase.
Vanilla не має research-hub на кільці; research-кільце бере energy/shield/maintenance.

Ring World секції
-----------------
Не змінюємо planet_size. while додасть райони, поки є слоти (зайве відсіє кап).
Типовий ванільний сегмент ≈ 10 районів. Є унікальні spec: alloys і energy.

Орбітальні депозити
-------------------
Не існує d_minerals_300 / d_physics_500 — тільки ванільні номінали, складені while.
Mining і research на ОДНОМУ тілі гра не змішує. Тому special розділено на два файли.
Living Metal / Nanites: фіксовані ID, без _100. Стакаємо 100 депозитів (×10 файли — 1000).
Unity: лише d_vast_unity_deposit (+3). Для ×300 — while count = 100; ×3000 — той самий блок ×10.
Astral threads: 33×3 + 1 = 100. Artifacts так само. ×10 файли повторюють блок 10 разів.
Станції: mining_* → Mining Station; science_* і research_* → Research Station.

Хабітат 4.x
-----------
1. run habitat_system_setup.txt (зірка)
2. run habitat_spawn_central.txt (нежила планета)
3. За бажанням major/minor на інших тілах з депозитами (більше районів)
4. Колонізуй Central Complex звичайним кораблем
5. run habitat_research.txt (або інший spec) на колонії

ignore_cap = yes лише на хабітаті, щоб забудувати після orbital-бонусів.
Fortress-district для хабітата у ванілі 4.x немає — фортеця через будівлі.

DLC (мінімум)
-------------
Utopia: Dyson, Ring World, Habitat, Nexus
Megacorp: Mega Art, Interstellar Assembly, Strategic Coordination, Mega Shipyard
Federations: Mega Shipyard (також), Mega Art stages
Ancient Relics: інколи perfection-арт (ми ставимо stage 3, без _4)
Overlord: Orbital Ring, Hyper Relay, Quantum Catapult
The Machine Age: Arc Furnace, Dyson Swarm
Cosmic Storms: Stellar Cannon
Nemesis: Matter Decompressor (також MegaCorp/Utopia combo залежно від патчу — MD з Nemesis)
Astral Planes: astral threads депозити
The Grand Archive: не спавнимо (немає підтвердженого complete ID)
Galaxy Edition / base: Gateway

Ризик видалити об'єкти
----------------------
system_dyson / system_ringworld: ванільна гра може знести внутрішні планети.
system_matter_decompressor / quantum_catapult: змінюють клас зірки.
Екуменополіс: planet_class pc_city перетворює світ; природні фічі city-worldу не личать.
Жоден файл не робить every_planet destroy навмисно.

Суперсистема (supersystem.txt)
-----------------------------
Виділи ЗІРКУ системи (не столичну). Скрипт СПОЧАТКУ зносить усі планети,
астероїди й мегасооруження в системі, ПОТІМ ставить 20 світів + 20 астероїдів.

4.x баланс (форуми / wiki 4.0–4.3): екуменополіс — міські роботи (сплави,
CG, наука, торгівля, єдність). Gaia — сільські райони (енергія, мінерали,
їжа) плюс наука і фортеця. По 2 планети кожної спеціалізації.

10 ecu size 78: Foundry / Factory / Research / Trade / Unity ×2
10 Gaia size 78: Energy / Mining / Food / Research / Fortress ×2
  На кожній Gaia: uncapped flags + lush/ultra_rich/magnetic/beauty/titanic/
  geothermal/microflora/hallucinogen_good + депозити generator/mining/farming.
Над кожною планетою: Orbital Ring tier 3 (habitation/gun/hangar/anchorage).
Попи ≈ 90% повної забудови (create_pop_group size). Clone vats на всіх світах.
20 астероїдів на зовнішній орбіті 360:
  5 science: фізика/соціум/інженерія по 500 + research-other (zro/DM/nanites/
    astral/artifacts/unity). Mining+research на одному тілі гра не змішує.
  10 basic: energy/minerals/food/alloys по 500
  5 rares: gases/crystals/motes/living metal/trade/artifacts_mining по 500
  Після survey скрипт ставить mining/research станції.
Цитадель: 3 hangar + 3 gun, defense_grid/uplink/jammer/command_center,
  3 ion cannon + large/small platforms. Hyper Relay біля зірки (немає стадії _0).
Недобудовані мега (майданчики _0 / перша стадія): Nexus, Sentry, SCC, Mega Art,
  Assembly, Shipyard, Gateway + Arc Furnace _1 на окремій molten.
  Dyson / Swarm / Ring / MD / Catapult / Cannon — окремі файли меню, бо
  не можуть стояти разом на одній зірці.
Техи: точково ecu/gaia/кільце/цитадель + T5 зброя/щити/реактори/strikecraft-3
  + dark matter FE-компоненти для ion cannon + 13 Pre-FTL insight + mega techs.
  Без research_all.
Захоплення: create_starbase citadel на гравця, який вводить код (is_ai = no).
Повторний запуск зносить і ставить заново.

Івент-система (eventsystem.txt)
------------------------------
Виділи зірку суперсистеми. Скрипт ставить НОВУ систему поряд (гіперлінія).
16 незаселених світів size 78. Не колонізує. Цитадель на id 0.

Планети під конкретні colony chains (ланцюг стартує ПІСЛЯ твоєї колонізації):
  Gaia — Subterranean; Continental — Titanic Life (рік 1), Doorway, Labyrinth,
  Odd Factory, Hallucinogen (рік 1); Tropical — Migrating Forests, Canopy dig;
  Ocean — Abandoned Terraforming, Nemma; Tomb — Underground Vault;
  Relic — Ancient Robot World; Desert — Living Snow; Savannah — Court of Blossoms;
  Tundra — Magnetic (рік 1); Arctic — Crystal Kraken.
На кожній: унікальний archaeology site, НЕ пройдений, без нагород.
Один незавершений Astral Rift. Ruined: Nexus, Sentry, Mega Art, Gateway.
Не видає event techs, Guardians, Enclaves, Paragons — це окремі файли/галактика.

Не комбінувати
--------------
megasystem_all_compatible НЕ з system_dyson, swarm, ringworld, catapult, stellar_cannon, MD.
system_dyson НЕ з swarm / cannon / catapult / ringworld на тій самій зірці.
orbital_resources_* / orbital_energy_* НЕ з orbital_science_* і special_research на тому ж тілі.
orbital_special_mining_* НЕ з science/research на тому ж тілі.
Різні ecu78_*_planet на одній планеті — ні, буде каша районів.
Різні habitat_* на одному хабітаті — ні (або свідомо поверх).
supersystem.txt — не запускати двічі в тій самій системі без потреби (знесе все знову).
eventsystem.txt — кожен запуск додає ще одну сусідню систему. Один раз.

Якщо команда падає
------------------
Консоль пише error. Частий випадок: не той scope (виділив флот замість зірки).
Orbital Ring модулі не встають, якщо виділена планета — виділи кільце.
space_owner порожній, якщо система не твоя — спочатку own / захопи базу.

Унікальні технології (не звичайне дерево)
----------------------------------------
Команда: research_technology <id>  (по одному рядку; виділення не потрібне).
НЕ використовується research_all_technologies.
Звичайні лазери/рейлгани/щити/броня/реактори/Destroyers/Cruisers/Battleships не видаються.

tech_insights.txt — НЕ запускати до achievement Insightful, якщо хочеш його зі спостереження Pre-FTL.
Trigger (vanilla): num_insight_techs >= 12. Це лічильник researched insight techs, не подія спостереження.
tech_insights_AFTER_achievement.txt — після Insightful.
tech_all_unique.txt — 128 безпечних унікальних ID (без insights, без відкриття L-Gate, без worm/covenant/cosmogenesis).
tech_lcluster_DANGEROUS.txt / tech_all_unique_DANGEROUS.txt — ламають сюжетні ланцюги.
Звіти: ACHIEVEMENT_WARNINGS.txt, UNIQUE_TECH_REPORT.txt, TECH_INSIGHTS_README.txt
  (їх не можна run — це текст).

Guardians / Precursors / Archaeology / Pre-FTL / L-Gates / Crises / Rifts
залишаються в галактиці. Скрипт дає лише technology researched.
"""


if __name__ == "__main__":
    main()
