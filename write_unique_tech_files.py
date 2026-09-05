#!/usr/bin/env python3
"""Generate Stellaris 4.x unique-tech run files from verified vanilla IDs.

Vanilla source (Aug 2026 install):
  ~/Library/Application Support/Steam/steamapps/common/Stellaris/common/technology/
Console command confirmed in stellaris binary: research_technology
Each run file is one command per line (Stellaris executes run files line-by-line).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

OUT = Path(__file__).resolve().parent / "run_scripts"
VANILLA = Path.home() / (
    "Library/Application Support/Steam/steamapps/common/Stellaris"
)
LOC_DIRS = [
    VANILLA / "localisation/english",
]


@dataclass
class Tech:
    tech_id: str
    name: str
    category: str
    gives: str
    source: str
    dlc: str
    prereqs: str
    in_deck: str
    can_miss: str
    flags: str
    achievement: str
    master: str


def load_loc_names() -> dict[str, str]:
    names: dict[str, str] = {}
    pattern = re.compile(r"^\s*([A-Za-z0-9_]+):\d*\s+\"(.+)\"\s*$")
    for loc_dir in LOC_DIRS:
        if not loc_dir.is_dir():
            continue
        for path in loc_dir.glob("*.yml"):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            for line in text.splitlines():
                match = pattern.match(line)
                if match:
                    names[match.group(1)] = match.group(2)
    return names


def grant_tech(tech_id: str) -> str:
    """give_technology ignores potential/prereqs. Scoped to the human player.

    Console research_technology fails with
    'Could not research prerequisite technology <same id>' when potential is false
    (DLC/flag/origin) or a listed prerequisite is missing.
    """
    return (
        "effect { random_playable_country = { limit = { is_ai = no } "
        f"give_technology = {{ tech = {tech_id} message = no }} }} }}"
    )


UNLOCK_FLAGS = (
    "effect { random_playable_country = { limit = { is_ai = no } "
    "set_country_flag = advanced_identity_creation "
    "set_country_flag = synth_queen_knowledge } }"
)

# Needed before unique mutations / bio integration; potential is DNA/beastmasters.
MUTATION_PREREQS = (
    "tech_alien_cloning",
    "tech_controlled_mutations",
    "tech_controlled_mutations_2",
)


def write_run(filename: str, tech_ids: list[str], *, flags: bool = False) -> None:
    seen: set[str] = set()
    lines: list[str] = []
    if flags:
        lines.append(UNLOCK_FLAGS)
    for tech_id in tech_ids:
        if tech_id in seen:
            continue
        seen.add(tech_id)
        lines.append(grant_tech(tech_id))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / filename).write_text("\n".join(lines), encoding="utf-8")


def loc(names: dict[str, str], tech_id: str) -> str:
    return names.get(tech_id, tech_id)


def main() -> None:
    names = load_loc_names()
    reports: list[Tech] = []

    def add(tech: Tech) -> None:
        if not tech.name or tech.name == tech.tech_id:
            tech.name = loc(names, tech.tech_id)
        reports.append(tech)

    insights = [
        "tech_unusual_senses",
        "tech_new_numbers",
        "tech_trinary_computing",
        "tech_atmospheric_orbital_mechanics",
        "tech_predatory_tactics",
        "tech_satisfying_insults",
        "tech_compact_living",
        "tech_alien_topography",
        "tech_xeno_aesthetics",
        "tech_lost_building_methods",
        "tech_supreme_alloy",
        "tech_ordered_retreat",
        "tech_temple_of_transportation",
    ]

    insight_details = {
        "tech_unusual_senses": (
            "envoys +0.25; Listening Posts +1 detection/sensor per 3 Detection Arrays"
        ),
        "tech_new_numbers": "envoys +0.25; +5% all research speed",
        "tech_trinary_computing": (
            "envoys +0.25; +10% espionage operation speed; -1 operation difficulty"
        ),
        "tech_atmospheric_orbital_mechanics": (
            "envoys +0.25; +5% mining/research stations; -50% station upkeep "
            "(nomad swap: waystation upkeep / stockpile)"
        ),
        "tech_predatory_tactics": "envoys +0.5; -50% sublight speed loss from cloaking",
        "tech_satisfying_insults": "envoys +0.5; +50% insult efficiency",
        "tech_compact_living": "envoys +0.5; -5% empire size penalty",
        "tech_alien_topography": (
            "envoys +0.5; +1 max districts on non-artificial worlds "
            "(void dweller/nomad: +1 artificial districts)"
        ),
        "tech_xeno_aesthetics": "envoys +0.5; +10% damage vs rivals",
        "tech_lost_building_methods": (
            "envoys +0.25; -30% empire size from districts; -30% district cost"
        ),
        "tech_supreme_alloy": "envoys +0.25; +0.25 alloys from metallurgists",
        "tech_ordered_retreat": "envoys +0.25; -15% MIA time",
        "tech_temple_of_transportation": "envoys +0.25; Hyper Relays produce +1 unity",
    }

    write_run("tech_insights.txt", insights)
    write_run("tech_insights_AFTER_achievement.txt", insights)
    for tech_id in insights:
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Insight / First Contact",
                insight_details[tech_id],
                "Observation Insights situation vs Pre-FTL (is_insight=yes, weight=0)",
                "First Contact",
                "none",
                "NO",
                "YES — only 12 of 13 needed; not all spawn in one galaxy",
                "is_insight=yes; no extra empire flag",
                "Insightful: num_insight_techs >= 12 (count only). Console usually disables Steam achievements. Do not run before natural Insightful if you want observation credit.",
                "NO — kept out of master because of Insightful",
            )
        )

    precursors = [
        "tech_secrets_cybrex",
        "tech_secrets_league",
        "tech_secrets_irassian",
        "tech_secrets_vultaum",
        "tech_secrets_yuht",
        "tech_secrets_baol",
        "tech_secrets_zroni",
    ]
    write_run("tech_precursors.txt", precursors)
    precursor_gives = {
        "tech_secrets_cybrex": "Secrets of the Cybrex archaeotech unlock (weight=0)",
        "tech_secrets_league": "Secrets of the First League; building uses this tech",
        "tech_secrets_irassian": "Secrets of the Irassians archaeotech unlock",
        "tech_secrets_vultaum": "Secrets of the Vultaum; building uses this tech",
        "tech_secrets_yuht": "Secrets of the Yuht archaeotech unlock",
        "tech_secrets_baol": "Secrets of the Baol; building uses this tech",
        "tech_secrets_zroni": "Secrets of the Zroni archaeotech unlock",
    }
    for tech_id in precursors:
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Precursor archaeotech secret",
                precursor_gives[tech_id],
                "Ancient Relics precursor chain / Minor Artifact 'Secrets of' action — mutually exclusive per campaign",
                "Ancient Relics",
                "none (weight=0 event grant)",
                "NO",
                "YES — only one precursor story per empire",
                "No chain flags set by this script. Relics not granted. Inetian/AdAkkaria have no tech_secrets_* IDs (they grant modifiers/relics + normal storm tech).",
                "Humility Before the Fall / other precursor achievements use country flags, not these techs",
                "YES",
            )
        )

    archaeotech = [
        "tech_archaeostudies",
        "tech_arcane_deciphering",
        "tech_archeology_lab_ancrel",
        "tech_archaeoshield",
        "tech_archaeoarmor",
        "tech_archaeo_detection_scrambler",
        "tech_archaeo_titan_beam",
        "tech_archaeo_pk_devolving_beam",
        "tech_archaeo_mass_drivers",
        "tech_archaeo_lasers",
        "tech_archaeo_point_defence",
        "tech_archaeo_missiles",
        "tech_archaeo_mass_accelerator",
        "tech_archaeo_strike_crafts",
        "tech_archaeo_rampart",
        "tech_archaeo_overcharger",
        "tech_archaeo_refinery",
    ]
    write_run("tech_archaeotech.txt", archaeotech)
    archaeo_notes = {
        "tech_archaeostudies": (
            "Gateway: Faculty of Archaeostudies. CAN appear after sites. "
            "Ship archaeocomponents check their own tech, not this one — Faculty needs this."
        ),
        "tech_arcane_deciphering": (
            "Unlocks Arcane Deciphering edict/decision. Needs Minor Artifacts in stock to appear naturally."
        ),
        "tech_archeology_lab_ancrel": "Curator Archaeology Lab (Ancient Relics version). Naturally curator-gated.",
        "tech_archaeoshield": "Ancient shields. Component prereq = this tech. Build cost uses Minor Artifacts.",
        "tech_archaeoarmor": "Ancient armor. Component prereq = this tech. Minor Artifacts to build.",
        "tech_archaeo_detection_scrambler": "Ancient utility / scrambler component.",
        "tech_archaeo_titan_beam": "Ancient titan weapon. Needs a titan hull to mount, not a flag.",
        "tech_archaeo_pk_devolving_beam": (
            "Ancient colossus weapon. Needs a Colossus to fire. No extra flag. AP Archaeoengineers only buffs, does not gate."
        ),
        "tech_archaeo_mass_drivers": "Ancient kinetics. Minor Artifacts to construct.",
        "tech_archaeo_lasers": "Ancient lasers. Minor Artifacts to construct.",
        "tech_archaeo_point_defence": "Ancient PD.",
        "tech_archaeo_missiles": "Ancient missiles.",
        "tech_archaeo_mass_accelerator": "Ancient XL kinetic.",
        "tech_archaeo_strike_crafts": "Ancient strike craft.",
        "tech_archaeo_rampart": "Ancient planetary/starbase defense building. No AP required to build.",
        "tech_archaeo_overcharger": "Ancient starbase module.",
        "tech_archaeo_refinery": "Ancient economic building.",
    }
    for tech_id in archaeotech:
        in_deck = (
            "YES (rare, after archaeology)"
            if tech_id in {"tech_archaeostudies", "tech_arcane_deciphering", "tech_archeology_lab_ancrel"}
            else "YES (rare, after archaeostudies; often missed)"
        )
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Archaeotechnology",
                archaeo_notes[tech_id],
                "Ancient Relics archaeology / Faculty / precursor secrets. Weights exist after archaeostudies but are easy to miss.",
                "Ancient Relics",
                "tech_archaeostudies listed as prereq on most; components check the specific archaeo tech",
                in_deck,
                "YES",
                "No empire flag required to USE ship components. Construction spends Minor Artifacts. ap_archaeoengineers only improves odds/stats, does not gate researched techs.",
                "Archaeologist achievement uses country flag from sites, not these techs",
                "YES",
            )
        )

    guardians = [
        "tech_dragon_armor",
        "tech_enigmatic_encoder",
        "tech_enigmatic_decoder",
        "tech_nanite_repair_system",
        "tech_nanite_autocannon",
        "tech_nanite_flak_batteries",
        "tech_leviathan_techgenesis",
        "tech_gargantuan_evolution",
    ]
    write_run("tech_guardians.txt", guardians)
    guardian_meta = {
        "tech_dragon_armor": (
            "Guardian / Leviathan",
            "Dragonscale Armor component (prereq = this tech only)",
            "Ether Drake / Shard / Sky Dragon outcomes or debris — weight=0",
            "Leviathans / Distant Stars",
            "Ether Drake achievements use kill flags (horror_killed etc.), not this tech",
        ),
        "tech_enigmatic_encoder": (
            "Guardian / Leviathan",
            "Enigmatic Encoder aux",
            "Enigmatic Fortress analysis/debris (events add_research_option) — weight=0",
            "Leviathans",
            "Fortress events/achievements use their own flags; script does not set guardian_killed",
        ),
        "tech_enigmatic_decoder": (
            "Guardian / Leviathan",
            "Enigmatic Decoder aux",
            "Enigmatic Fortress — weight=0",
            "Leviathans",
            "Same as encoder",
        ),
        "tech_nanite_repair_system": (
            "Guardian / Leviathan",
            "Nanite Repair System aux",
            "Scavenger Bot debris only (weight_modifier factor=0)",
            "Distant Stars",
            "Kill/debris achievements use flags, not this tech",
        ),
        "tech_nanite_autocannon": (
            "Guardian / Leviathan",
            "Nanite Autocannon",
            "Scavenger Bot reverse engineering",
            "Distant Stars",
            "Kill flags not set",
        ),
        "tech_nanite_flak_batteries": (
            "Guardian / Leviathan",
            "Nanite Flak Battery",
            "Scavenger Bot reverse engineering",
            "Distant Stars",
            "Kill flags not set",
        ),
        "tech_leviathan_techgenesis": (
            "Guardian / Leviathan",
            "Leviathan-derived machine component unlock (Machine Age event grant, weight factor=0)",
            "Leviathan events while Machine Age DLC is active",
            "The Machine Age + Leviathans",
            "Event-granted; this script does not complete leviathan events",
        ),
        "tech_gargantuan_evolution": (
            "Guardian / Leviathan",
            "+5% job energy (Voidspawn-related Distant Stars grant, weight=0)",
            "distant_stars_events_3 add_research_option",
            "Distant Stars",
            "Voidspawn content uses its own flags",
        ),
    }
    for tech_id in guardians:
        cat, gives, source, dlc, ach = guardian_meta[tech_id]
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                cat,
                gives,
                source,
                dlc,
                "none",
                "NO",
                "YES",
                "No guardian_killed / restored_dreadnought flags",
                ach,
                "YES",
            )
        )

    fallen = [
        "tech_dark_matter_deflector",
        "tech_dark_matter_power_core",
        "tech_dark_matter_propulsion",
        "tech_cloaking_dark_matter",
        "tech_fe_affluence_1",
        "tech_fe_affluence_2",
        "tech_fe_nourishment_1",
        "tech_fe_nourishment_2",
        "tech_fe_fabricator_1",
        "tech_fe_fabricator_2",
        "tech_fe_singularity_1",
        "tech_fe_singularity_2",
        "tech_fe_forge_1",
        "tech_fe_forge_2",
        "tech_fe_dome_1",
        "tech_fe_dome_2",
        "tech_fe_fortress_1",
        "tech_fe_fortress_2",
        "tech_fe_administration_1",
        "tech_fe_administration_2",
        "tech_fe_assembly_1",
        "tech_fe_assembly_2",
        "tech_fe_clinic_1",
        "tech_fe_clinic_2",
        "tech_fe_security_1",
        "tech_fe_security_2",
        "tech_fe_market_1",
        "tech_fe_market_2",
        "tech_fe_silo_1",
        "tech_fe_silo_2",
        "tech_fe_entertainment_1",
        "tech_fe_entertainment_2",
        "tech_fe_lab_1",
        "tech_fe_lab_2",
        "tech_fe_mine_1",
        "tech_fe_mine_2",
    ]
    write_run("tech_fallen_empire.txt", fallen)
    for tech_id in fallen:
        extra = ""
        if tech_id == "tech_cloaking_dark_matter":
            extra = (
                " Component prereq is this tech. Natural draw wants cloaking_3 + DM deflectors; "
                "those are NOT granted. Cloak module still checks this ID."
            )
        if tech_id.startswith("tech_fe_"):
            extra = (
                " Building unlock. Gestalt/individual restrictions still apply to some buildings "
                "(assembly/clinic/market/entertainment). Enigmatic Engineering is only for drawing, not using."
            )
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Fallen / Awakened Empire",
                "FE-exclusive component or building" + extra,
                "FE/AE debris, Enigmatic Engineering draw, or Cosmogenesis — player weight is effectively 0 without those",
                "Utopia / First Contact (DM cloak) / base FE",
                "Vanilla lists shields_5 / zero_point / thrusters_4 / cloaking_3 for some; not granted. Components check the unique tech.",
                "NO for player without EE/Cosmogenesis",
                "YES",
                "Each researched FE tech stacks FE opinion penalty in vanilla. No crisis/AP flags set.",
                "Outside Context uses country flag outsidecontext, not these techs",
                "YES",
            )
        )

    crisis = [
        "tech_extradimensional_weapon_1",
        "tech_scourge_missile_1",
        "tech_swarm_strike_craft_1",
        "tech_synth_queen_knowledge",
        "tech_nanite_repair_system_synth_queen",
    ]
    write_run("tech_crisis.txt", crisis, flags=True)
    crisis_meta = {
        "tech_extradimensional_weapon_1": (
            "Matter Disintegrator. Deck weight 0 unless covenant_end_of_the_cycle; also Unbidden/Horror debris. Script does not set EotC.",
            "Leviathans / Utopia / crisis debris",
        ),
        "tech_scourge_missile_1": (
            "Prethoryn Scourge missiles. weight=0 reverse engineering.",
            "Utopia crisis",
        ),
        "tech_swarm_strike_craft_1": (
            "Prethoryn swarm strike craft. weight=0 reverse engineering.",
            "Utopia crisis",
        ),
        "tech_synth_queen_knowledge": (
            "Cetana's Thought. potential requires country flag synth_queen_knowledge to APPEAR; researched tech still grants its modifier if given.",
            "The Machine Age (Cetana)",
        ),
        "tech_nanite_repair_system_synth_queen": (
            "Cetana nanite repair component. weight=0. Distinct from Scavenger tech_nanite_repair_system.",
            "The Machine Age (Cetana)",
        ),
    }
    for tech_id in crisis:
        gives, dlc = crisis_meta[tech_id]
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Crisis reverse-engineering",
                gives,
                "Crisis debris / Cetana events — not granted by starting a crisis here",
                dlc,
                "none granted",
                "NO",
                "YES",
                "No crisis start flags. EotC flag not set. Cosmogenesis path techs are in DANGEROUS only.",
                "Crisis achievements use their own flags/kills",
                "YES",
            )
        )

    lcluster_safe = [
        "tech_nanite_transmutation",
        "tech_neuroregeneration",
    ]
    write_run("tech_lcluster.txt", lcluster_safe)
    add(
        Tech(
            "tech_nanite_transmutation",
            loc(names, "tech_nanite_transmutation"),
            "L-Cluster / Nanites",
            "Nanite transmutation (strategic resource processing). Appears only after nanite deposits in borders.",
            "Distant Stars nanite deposits / L-Cluster aftermath — does not open L-Gates",
            "Distant Stars",
            "none",
            "NO until nanites found",
            "YES if L-Cluster never yields nanites",
            "No l_cluster_opened flag",
            "L-Gate achievements use global/country flags, not this tech",
            "YES",
        )
    )
    add(
        Tech(
            "tech_neuroregeneration",
            loc(names, "tech_neuroregeneration"),
            "L-Cluster / unique system",
            "+25% leader XP, +10 leader lifespan (weight=0 sealed-system reward)",
            "Distant Stars sealed system / related events",
            "Distant Stars",
            "none",
            "NO",
            "YES",
            "Does not activate L-Gates",
            "Low — event flags not set",
            "YES",
        )
    )

    lcluster_danger = [
        "tech_lgate_activation",
        "tech_repeatable_lcluster_clue",
    ]
    write_run("tech_lcluster_DANGEROUS.txt", lcluster_danger)
    add(
        Tech(
            "tech_lgate_activation",
            loc(names, "tech_lgate_activation"),
            "L-Cluster DANGEROUS",
            "L-Gate Activation. Events (distant_stars_events_3) check has_technology = tech_lgate_activation to progress opening.",
            "L-Gate insight special project",
            "Distant Stars",
            "none",
            "NO (weight=0; potential while cluster closed)",
            "YES",
            "Researching this is the vanilla unlock used to open L-Gates. Do not run if you want a closed cluster.",
            "HIGH — can skip/short-circuit L-Gate chain",
            "NO",
        )
    )
    add(
        Tech(
            "tech_repeatable_lcluster_clue",
            loc(names, "tech_repeatable_lcluster_clue"),
            "L-Cluster DANGEROUS",
            "Repeatable L-Cluster clue research. Grants clues toward opening.",
            "L-Gate insight loop",
            "Distant Stars",
            "none",
            "NO until L-Gate chain started",
            "YES",
            "Advances L-Gate clue count",
            "HIGH — progresses L-Gate chain",
            "NO",
        )
    )

    psionic_safe = [
        "tech_psionic_barrier",
        "tech_psionic_shield",
        "tech_psionic_bombers",
        "tech_psionic_lightning",
        "tech_psionic_disruptor",
        "tech_zro_launcher",
        "tech_materiality_engine",
        "tech_aura_resonation",
        "tech_cloaking_psi",
        "tech_psi_jump_drive_1",
    ]
    write_run("tech_psionic_event.txt", psionic_safe)
    psionic_meta = {
        "tech_psionic_barrier": "Psionic barrier component. weight=0 shroud/event. No ethics change.",
        "tech_psionic_shield": "Psionic shield component. weight=0.",
        "tech_psionic_bombers": "Shroud event strike craft. weight=0.",
        "tech_psionic_lightning": "Shroud event weapon. weight=0.",
        "tech_psionic_disruptor": "Shroud event weapon. weight=0.",
        "tech_zro_launcher": "Shroud event weapon. weight=0.",
        "tech_materiality_engine": "Materiality Engine unlock. weight=0 event. Building still needs to be constructed.",
        "tech_aura_resonation": "Psionic Projector unlock. weight=0. Does not set covenant.",
        "tech_cloaking_psi": "Psi cloak. Natural prereq tech_psi_jump_drive_1 not required for the component ID.",
        "tech_psi_jump_drive_1": (
            "Psi Jump Drive. Can appear after precognition for psionic empires; practically unavailable to materialists. "
            "feature_flags jump_method. Does not set shroud covenant or End of the Cycle."
        ),
    }
    for tech_id in psionic_safe:
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Psionic / Shroud event",
                psionic_meta[tech_id],
                "Shroud DLC events / psi tree (jump drive)",
                "Utopia / The Shroud / First Contact (psi cloak)",
                "Vanilla lists psi theory / precognition; not granted except the unique techs themselves",
                "NO for most; psi jump CONDITIONAL for psionic empires",
                "YES especially as Materialist",
                "No ethics, AP, covenant, or EotC flags",
                "Shroud/covenant achievements use other flags",
                "YES",
            )
        )

    rare_res = [
        "tech_mine_living_metal",
        "tech_mine_zro",
        "tech_mine_dark_matter",
        "tech_astral_harvesting",
    ]
    write_run("tech_rare_resources.txt", rare_res)
    rare_meta = {
        "tech_mine_living_metal": (
            "Living Metal mining. Weight 0 until a living metal deposit is in borders (or nomad harvest).",
            "base / Ancient Relics deposits",
        ),
        "tech_mine_zro": (
            "Zro distillation. Rare; weight 0 without zro in borders / relations.",
            "Utopia / Shroud",
        ),
        "tech_mine_dark_matter": (
            "Dark Matter drawing. Weight 0 without dark matter deposits (often black holes).",
            "Leviathans / Utopia",
        ),
        "tech_astral_harvesting": (
            "Unlocks astral thread actions. Weight 0 until threads/rifts found or a relation has the tech.",
            "Astral Planes",
        ),
    }
    for tech_id, (gives, dlc) in rare_meta.items():
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Rare strategic resource",
                gives,
                "Must discover the resource first in a normal game",
                dlc,
                "sensors/space construction listed in vanilla; not granted",
                "NO until deposit found",
                "YES",
                "Does not spawn deposits. Resourceful achievement needs monthly income, not these techs.",
                "Resourceful is income-based",
                "YES",
            )
        )

    events_unique = [
        "tech_curator_lab",
        "tech_archeology_lab",
        "tech_orbital_trash_dispersal",
        "tech_strike_craft_skrand",
        "tech_starfire_cannon",
        "null_void_beam",
        "tech_boarding_cables",
        "tech_enhanced_cryosleep_sedatives",
        "tech_universal_marcophage",
        "tech_pyroclastic_resonation",
        "tech_alloy_fossilization",
        "tech_orbital_maneuvers",
        "tech_cryovault",
        "tech_living_test_subjects",
        "tech_georadiation_terraforming",
        "tech_identity_copy",
        "tech_identity_fusion",
        "tech_identity_initialization",
    ]
    write_run("tech_events_unique.txt", events_unique, flags=True)
    events_meta = {
        "tech_curator_lab": ("Curator Insights Lab. Deck factor=0 without curator scientist or curator_insight.", "Leviathans"),
        "tech_archeology_lab": ("Archaeology Lab (non-Ancient Relics). Curator-gated. potential has_ancrel=no.", "Leviathans"),
        "tech_orbital_trash_dispersal": ("Trash Disperser. weight=0 Caravan Fleet 3 deal only.", "MegaCorp"),
        "tech_strike_craft_skrand": ("Skrand strike craft. weight=0 Paragon legendary story.", "Galactic Paragons"),
        "tech_starfire_cannon": (
            "Starfire Cannon. potential origin_red_giant AND country flag starfire_cannon_unlocked. "
            "Tech can be researched via console, but the weapon decision still checks origin/flag.",
            "The Shroud / Infernal origin",
        ),
        "null_void_beam": ("Null Void Beam. weight=0 colony event grant (colony_events_3).", "base event"),
        "tech_boarding_cables": ("Boarding Cables aux. weight=0 Grand Archive origin/pirate event.", "The Grand Archive"),
        "tech_enhanced_cryosleep_sedatives": ("Strange Worlds event tech. weight=0.", "The Shroud / Strange Worlds"),
        "tech_universal_marcophage": ("Strange Worlds rare event tech. weight=0.", "The Shroud / Strange Worlds"),
        "tech_pyroclastic_resonation": ("Infernal Tornadoes anomaly. weight=0.", "The Shroud / Extreme Frontiers"),
        "tech_alloy_fossilization": ("Chthonian Preservation anomaly. weight=0.", "The Shroud / Extreme Frontiers"),
        "tech_orbital_maneuvers": ("+10% ship speed. Orbital Resonance anomaly. weight=0.", "The Shroud / Extreme Frontiers"),
        "tech_cryovault": ("Absolute Zero archaeology. weight=0. potential is_nomadic=no.", "The Shroud / Extreme Frontiers"),
        "tech_living_test_subjects": ("-5% society tech cost. Toxic Matrix site. weight=0.", "The Shroud / Extreme Frontiers"),
        "tech_georadiation_terraforming": ("Georadiation terraforming chain. weight=0.", "The Shroud / Extreme Frontiers"),
        "tech_identity_copy": (
            "Synthetic identity Copy policy. weight=0 Machine Age script. Policy may still want origin/situation context.",
            "The Machine Age",
        ),
        "tech_identity_fusion": (
            "Identity Fusion. potential has_country_flag=advanced_identity_creation to appear; flag is NOT set here.",
            "The Machine Age",
        ),
        "tech_identity_initialization": (
            "Identity Initialization. Same flag as fusion for natural draw. Flag not set.",
            "The Machine Age",
        ),
    }
    for tech_id in events_unique:
        gives, dlc = events_meta[tech_id]
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Unique event / origin / enclave",
                gives,
                "Anomaly, archaeology, enclave, origin, or unique leader — not guaranteed",
                dlc,
                "none granted",
                "NO",
                "YES",
                "starfire / identity fusion may need extra flags to fully function",
                "Origin/event achievements use flags, not these techs",
                "YES",
            )
        )

    fauna = [
        *MUTATION_PREREQS,
        "tech_amoeba_strike_craft_1",
        "tech_regenerative_hull_tissue",
        "tech_crystal_armor_1",
        "tech_crystal_armor_2",
        "tech_mining_drone_weapon_1",
        "tech_space_cloud_weapon_1",
        "tech_space_whale_weapon_1",
        "tech_voidworm_immunity",
        "tech_asteroidal_carapace",
        "tech_unique_mutation_space_amoeba",
        "tech_unique_mutation_tiyanki",
        "tech_unique_mutation_voidworm",
        "tech_unique_mutation_cutholoid",
        "tech_unique_mutation_crystalline_entity",
        "tech_unique_mutation_restorative_enzymes",
        "tech_unique_mutation_starborne_biology",
        "tech_thrusters_bio_integration",
        "tech_hyper_drive_bio_integration",
        "tech_sensors_bio_integration",
        "tech_combat_computers_bio_integration",
    ]
    write_run("tech_space_fauna.txt", fauna)
    fauna_gives = {
        "tech_amoeba_strike_craft_1": "Amoeba flagella strike craft. weight=0 first contact/debris.",
        "tech_regenerative_hull_tissue": "Regenerative hull. weight_modifier factor=0 reverse engineering only.",
        "tech_crystal_armor_1": "Crystal-Infused Plating. weight=0; flag crystal_armor_1_weight can add draw.",
        "tech_crystal_armor_2": "Crystal-Forged Plating. weight=0 Crystal Nidus / later contact.",
        "tech_mining_drone_weapon_1": "Mining drone laser. weight=0.",
        "tech_space_cloud_weapon_1": "Cloud lightning. weight=0.",
        "tech_space_whale_weapon_1": "Tiyanki energy siphon. weight=0 first contact.",
        "tech_voidworm_immunity": "Voidworm vaccine / damage vs voidworms. weight=0 Grand Archive.",
        "tech_asteroidal_carapace": "Cutholoid first-contact carapace. weight=0.",
        "tech_unique_mutation_space_amoeba": "Unique fauna mutation component. weight=0. Mutation SLOTS still need controlled_mutations tree to use vivarium mutations fully.",
        "tech_unique_mutation_tiyanki": "Unique Tiyanki mutation. weight=0.",
        "tech_unique_mutation_voidworm": "Unique Voidworm mutation. weight=0.",
        "tech_unique_mutation_cutholoid": "Unique Cutholoid mutation. weight=0.",
        "tech_unique_mutation_crystalline_entity": "Unique crystal mutation. weight=0.",
        "tech_unique_mutation_restorative_enzymes": "Unique restorative enzymes mutation. weight=0.",
        "tech_unique_mutation_starborne_biology": "Unique starborne biology mutation. weight=0.",
        "tech_thrusters_bio_integration": "Fauna core thruster integration. weight=0. Listed prereq controlled_mutations not granted.",
        "tech_hyper_drive_bio_integration": "Fauna hyperdrive integration. weight=0.",
        "tech_sensors_bio_integration": "Fauna sensor integration. weight=0.",
        "tech_combat_computers_bio_integration": "Fauna combat computer integration. weight=0.",
    }
    for tech_id in fauna:
        if tech_id not in fauna_gives:
            continue
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "Space fauna",
                fauna_gives[tech_id],
                "Space fauna first contact / debris / Grand Archive DNA — fauna not destroyed by this script",
                "base / The Grand Archive",
                "unique mutations list controlled_mutations_2; not granted",
                "NO",
                "YES — fauna may never spawn or be contacted",
                "No fauna-killed flags",
                "Tiyanki/wraith/horror achievements are kill flags",
                "YES",
            )
        )

    astral = [
        "tech_rift_sphere",
    ]
    write_run("tech_astral.txt", astral)
    add(
        Tech(
            "tech_rift_sphere",
            loc(names, "tech_rift_sphere"),
            "Astral Planes",
            "Rift Sphere. weight=0. feature_flags unlock_astral_rift_exploration — lets you explore rifts when found; does not complete rifts or set rift outcome flags.",
            "First Astral Rift contact",
            "Astral Planes",
            "none",
            "NO",
            "YES",
            "Unlocks exploration capability only",
            "Rift achievements use event flags",
            "YES",
        )
    )

    dangerous = [
        "tech_lgate_activation",
        "tech_repeatable_lcluster_clue",
        "tech_akx_worm_1",
        "tech_akx_worm_2",
        "tech_akx_worm_3",
        "tech_covenant_composer",
        "tech_covenant_eater",
        "tech_covenant_instrument",
        "tech_covenant_cradle",
        "tech_covenant_whisperers",
        "tech_psionic_aura",
        "tech_aura_intensification",
        "tech_psionic_suppression",
        "tech_cosmogenesis_crisis_1",
        "tech_cosmogenesis_crisis_2",
        "tech_cosmogenesis_crisis_3",
        "tech_cosmogenesis_crisis_4",
        "tech_cosmogenesis_crisis_5",
        "tech_cosmogenesis_escort",
        "tech_cosmogenesis_battlecruiser",
        "tech_cosmogenesis_weaver",
        "tech_cosmogenesis_mauler",
        "tech_cosmogenesis_harbinger",
        "tech_cosmogenesis_stinger",
        "tech_cosmogenesis_world",
        "tech_cosmogenesis_thesis",
    ]
    write_run("tech_all_unique_DANGEROUS.txt", dangerous)
    danger_why = {
        "tech_akx_worm_1": "Horizon Signal events branch on has_technology = tech_akx_worm_*. Pre-granting can skip or break the chain (What Was Will Be uses worm_awaited flag).",
        "tech_akx_worm_2": "Horizon Signal society worm tech. Same event checks.",
        "tech_akx_worm_3": "Horizon Signal end-stage worm tech. Same event checks.",
        "tech_covenant_composer": "Covenant reward tech. Mutually exclusive covenant outcomes; do not grant all as if all covenants were signed.",
        "tech_covenant_eater": "Covenant reward tech.",
        "tech_covenant_instrument": "Covenant reward tech.",
        "tech_covenant_cradle": "Covenant reward tech.",
        "tech_covenant_whisperers": "Covenant reward tech.",
        "tech_psionic_aura": "feature_flags unlock_psionic_aura — changes Shroud aura availability without being psionic.",
        "tech_aura_intensification": "feature_flags allow aura intensity spread/growth.",
        "tech_psionic_suppression": "potential has_encountered_psionic_auras; anti-aura toolkit.",
        "tech_cosmogenesis_crisis_1": "Cosmogenesis crisis path level. Changes ascension/crisis progression.",
        "tech_cosmogenesis_crisis_2": "Cosmogenesis path.",
        "tech_cosmogenesis_crisis_3": "Cosmogenesis path.",
        "tech_cosmogenesis_crisis_4": "Cosmogenesis path.",
        "tech_cosmogenesis_crisis_5": "Cosmogenesis path.",
        "tech_cosmogenesis_escort": "Cosmogenesis FE-style ship.",
        "tech_cosmogenesis_battlecruiser": "Cosmogenesis FE-style ship.",
        "tech_cosmogenesis_weaver": "Cosmogenesis bioship.",
        "tech_cosmogenesis_mauler": "Cosmogenesis bioship.",
        "tech_cosmogenesis_harbinger": "Cosmogenesis bioship.",
        "tech_cosmogenesis_stinger": "Cosmogenesis bioship.",
        "tech_cosmogenesis_world": "Cosmogenesis world / lathe-related.",
        "tech_cosmogenesis_thesis": "Applied Infinity Thesis — Keepers of Knowledge interaction.",
        "tech_lgate_activation": "Opens L-Gate progression.",
        "tech_repeatable_lcluster_clue": "Adds L-Gate clues.",
    }
    already = {t.tech_id for t in reports}
    for tech_id in dangerous:
        if tech_id in already:
            continue
        add(
            Tech(
                tech_id,
                loc(names, tech_id),
                "DANGEROUS unique",
                danger_why.get(tech_id, "See DANGEROUS file warning"),
                "Event / crisis / shroud / L-Gate",
                "varies",
                "none granted",
                "NO / path-locked",
                "YES",
                danger_why.get(tech_id, ""),
                "HIGH — chain/path/covenant",
                "NO",
            )
        )

    master = []
    for group in (
        precursors,
        archaeotech,
        guardians,
        fallen,
        crisis,
        lcluster_safe,
        psionic_safe,
        rare_res,
        events_unique,
        fauna,
        astral,
    ):
        master.extend(group)
    write_run("tech_all_unique.txt", master, flags=True)
    write_run("tech_all_specific.txt", list(insights) + master, flags=True)

    write_reports(reports, insight_details)
    print(f"Wrote unique-tech run files to {OUT}")
    print(f"Master unique techs: {len(list(dict.fromkeys(master)))}")
    print(f"Report rows: {len(reports)}")


def write_reports(reports: list[Tech], insight_details: dict[str, str]) -> None:
    warn = []
    warn.append("ACHIEVEMENT WARNINGS — Stellaris 4.x vanilla common/achievements.txt")
    warn.append("Triggers verified in the local install. Console/run typically makes the save ineligible for Steam achievements; that is separate from the scripted trigger.")
    warn.append("")
    warn.append("Technology | Achievement | Risk | What to do")
    warn.append("---------- | ----------- | ---- | ----------")
    warn.append(
        "All 13 Insight techs | Insightful (id 159) | HIGH | Trigger is only `num_insight_techs >= 12` (First Contact). It does NOT check observation source. Giving 13 via console would satisfy the count IF achievements were still eligible. Steam: using console usually disables achievements on that save. If you want Insightful from Pre-FTL observation on a clean Ironman path: get it first, then run tech_insights_AFTER_achievement.txt. Do NOT run tech_insights.txt before that."
    )
    warn.append(
        "tech_dragon_armor / leviathan techs | Whence It Came / Wraith / Tiyanki / Dreadnought / etc. | LOW for the tech, HIGH if you kill | Achievements check flags (horror_killed, killed_wraith, tiyanki_killed, restored_dreadnought). This pack does not set those flags. Guardians stay alive. You can still earn kill/restore achievements later."
    )
    warn.append(
        "tech_secrets_* | precursor story achievements (e.g. Humility Before the Fall = completed_inetian_traders_precursor) | LOW | Those achievements check precursor completion flags / relics, not Secrets techs. Inetian/AdAkkaria have no secret-tech IDs."
    )
    warn.append(
        "Archaeotechs | Archaeologist (id 99) | LOW | Trigger is has_country_flag = archaeologist_achievement (sites), not researching archaeotechs."
    )
    warn.append(
        "tech_akx_worm_* | What Was, Will Be (worm_awaited) | HIGH | Horizon Signal events test has_technology = tech_akx_worm_*. Pre-granting can skip chain steps. Only in DANGEROUS file."
    )
    warn.append(
        "tech_lgate_activation / clue repeatable | L-Gate / Distant Stars chain achievements | HIGH | Opening progression uses these techs. Only in DANGEROUS."
    )
    warn.append(
        "tech_covenant_* | Shroud covenant achievements | HIGH | Mutually exclusive covenant rewards. Only in DANGEROUS."
    )
    warn.append(
        "tech_cosmogenesis_* | Cosmogenesis / crisis path | HIGH | These ARE the path. Only in DANGEROUS."
    )
    warn.append(
        "tech_mine_living_metal / zro / dark_matter | Resourceful | NONE from tech alone | Resourceful checks monthly income of those resources, not the techs."
    )
    warn.append(
        "Any research_technology via console | Steam achievements in general | HIGH | Using the console/run command is treated as a cheat by Steam for that save. This is not unique to Insightful."
    )
    (OUT / "ACHIEVEMENT_WARNINGS.txt").write_text("\n".join(warn) + "\n", encoding="utf-8")

    lines = [
        "UNIQUE TECH REPORT — Stellaris 4.x vanilla (local install August 2026)",
        "IDs taken from common/technology/*.txt. Names from localisation/english.",
        "research_all_technologies is never used.",
        "Normal weapons/armor/shields/reactors/destroyers/cruisers/battleships/economy tree are excluded.",
        "Console command: research_technology <id>  (present in stellaris binary; applies to player, no selection needed).",
        "do NOT use multi-line effect blocks in these files.",
        "",
        "Insightful trigger (verbatim):",
        "  achievement_insightful = { possible = { has_first_contact_dlc = yes } happened = { num_insight_techs >= 12 } }",
        "There are 13 is_insight=yes techs in 00_first_contact_tech.txt.",
        "",
        "Cosmic Storms precursors Inetian Traders and AdAkkaria: no tech_secrets_* IDs.",
        "Their vanilla rewards are modifiers/relics and (Inetian) tech_storm_manipulation, which is a normal storm tech — not granted here.",
        "",
        "Archaeotech extra requirements:",
        "  Ship components: has_technology = the specific archaeo tech. Minor Artifacts are a BUILD cost, not a flag.",
        "  Faculty of Archaeostudies: needs tech_archaeostudies.",
        "  ap_archaeoengineers: buffs, does not gate an already researched tech.",
        "  Colossus/Titan weapons still need those ship sizes to mount.",
        "",
        "================================================================",
        "",
    ]
    for tech in reports:
        lines.extend(
            [
                f"Technology ID: {tech.tech_id}",
                f"Name: {tech.name}",
                f"Category: {tech.category}",
                f"What it gives: {tech.gives}",
                f"Natural source: {tech.source}",
                f"DLC: {tech.dlc}",
                f"Prerequisites: {tech.prereqs}",
                f"Can normally appear in tech deck: {tech.in_deck}",
                f"Can be missed in one campaign: {tech.can_miss}",
                f"Event/flag dependency: {tech.flags}",
                f"Achievement risk: {tech.achievement}",
                f"Included in master file: {tech.master}",
                "",
            ]
        )

        names = {t.tech_id: t.name for t in reports}
    insight_readme = [
        "INSIGHT TECHNOLOGIES (First Contact) — 13 techs verified in 00_first_contact_tech.txt",
        "Natural source: Observation Insights situation vs Pre-FTL.",
        "DLC: First Contact. weight=0, is_insight=yes.",
        "",
        "Achievement Insightful (common/achievements.txt):",
        "  possible = { has_first_contact_dlc = yes }",
        "  happened = { num_insight_techs >= 12 }",
        "It does not require that the techs came from observation.",
        "It does not check flags. It is a count of researched insight technologies.",
        "",
        "Do NOT run tech_insights.txt before Insightful if you want to earn it on a non-cheated Ironman save.",
        "Use tech_insights_AFTER_achievement.txt after you already have Insightful (same 13 IDs, idempotent).",
        "",
        "ID | Name | Bonus | Counts for Insightful",
    ]
    for tech_id, bonus in insight_details.items():
        insight_readme.append(
            f"{tech_id} | {names.get(tech_id, tech_id)} | {bonus} | YES"
        )
    (OUT / "TECH_INSIGHTS_README.txt").write_text("\n".join(insight_readme) + "\n", encoding="utf-8")
    (OUT / "UNIQUE_TECH_REPORT.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
