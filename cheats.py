"""Stellaris console cheats for the overlay widget."""

from __future__ import annotations

from dataclasses import dataclass, replace

from run_scripts import RUN_SCRIPTS, run_command


@dataclass(frozen=True)
class Cheat:
    command: str
    title: str
    description: str
    category: str
    variants: tuple[Cheat, ...] = ()


def _v(command: str, title: str, description: str = "") -> Cheat:
    return Cheat(command, title, description, "")


@dataclass(frozen=True)
class HarvestResource:
    label: str
    category: str
    station: str
    id_prefix: str = ""
    fixed_id: str = ""
    amounts: tuple[int, ...] = ()

    def deposit_id(self, amount: int | None = None) -> str:
        if self.fixed_id:
            return self.fixed_id
        value = amount if amount is not None else (self.amounts[-1] if self.amounts else 1)
        return f"{self.id_prefix}_{value}"

    def command(self, amount: int | None = None) -> str:
        return f"effect add_deposit = {self.deposit_id(amount)}"


HARVEST_RESOURCES: tuple[HarvestResource, ...] = (
    HarvestResource("Енергія", "Звичайні", "mining", id_prefix="d_energy", amounts=tuple(range(1, 11))),
    HarvestResource("Мінерали", "Звичайні", "mining", id_prefix="d_minerals", amounts=tuple(range(1, 11))),
    HarvestResource("Їжа", "Звичайні", "mining", id_prefix="d_food", amounts=(3, 10)),
    HarvestResource("Сплави", "Звичайні", "mining", id_prefix="d_alloys", amounts=(1, 2, 3, 4, 5, 10, 25)),
    HarvestResource("Торгівля", "Звичайні", "mining", id_prefix="d_trade_value", amounts=tuple(range(1, 11))),
    HarvestResource("Екзотичні гази", "Стратегічні", "mining", id_prefix="d_exotic_gases", amounts=(1, 2, 3, 4, 5)),
    HarvestResource("Рідкісні кристали", "Стратегічні", "mining", id_prefix="d_rare_crystals", amounts=(1, 2, 3, 4, 5)),
    HarvestResource("Нестабільні частинки", "Стратегічні", "mining", id_prefix="d_volatile_motes", amounts=(1, 2, 3, 4, 5)),
    HarvestResource("Живий метал", "Стратегічні", "mining", fixed_id="d_living_metal_deposit"),
    HarvestResource("Артефакти (шахта)", "Стратегічні", "mining", id_prefix="d_artifacts_mining", amounts=(1, 2, 3)),
    HarvestResource("Фізика", "Дослідження", "research", id_prefix="d_physics", amounts=tuple(range(1, 11))),
    HarvestResource("Суспільство", "Дослідження", "research", id_prefix="d_society", amounts=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15)),
    HarvestResource("Інженерія", "Дослідження", "research", id_prefix="d_engineering", amounts=tuple(range(1, 11))),
    HarvestResource("Темна матерія", "Дослідження", "research", id_prefix="d_dark_matter_deposit", amounts=(1, 2, 3, 10)),
    HarvestResource("Зро", "Дослідження", "research", id_prefix="d_zro_deposit", amounts=(1, 2, 3, 4, 5)),
    HarvestResource("Артефакти (наука)", "Дослідження", "research", id_prefix="d_artifacts_research", amounts=(1, 2, 3)),
    HarvestResource("Астральні нитки", "Дослідження", "research", id_prefix="d_astral_threads_deposit", amounts=(1, 2, 3)),
    HarvestResource("Єдність", "Дослідження", "research", fixed_id="d_vast_unity_deposit"),
    HarvestResource("Наніти", "Дослідження", "research", fixed_id="d_nanites_deposit"),
)


def _harvest_variants() -> tuple[Cheat, ...]:
    station_uk = {"mining": "mining station", "research": "research station"}
    items: list[Cheat] = []
    for resource in HARVEST_RESOURCES:
        amount = resource.amounts[-1] if resource.amounts else None
        extra = f"{station_uk[resource.station]}. Макс. видобуток."
        items.append(_v(resource.command(amount), resource.label, extra))
    return tuple(items)


_POP_CMD = (
    "effect every_owned_pop_group = {{ limit = {{ id = POP_GROUP_ID }} {action} = {{ {slot} }} }}"
)


def _pop_add(trait: str) -> str:
    return _POP_CMD.format(action="add_trait", slot=f"trait = {trait}")


def _pop_remove(trait: str) -> str:
    return _POP_CMD.format(action="remove_trait", slot=f"trait = {trait}")


def _pop_trait_variants() -> tuple[Cheat, ...]:  # noqa: PLR0912
    # Усі видові трейти з папки common/traits/ (species-only, не лідерські).
    # cost= — скільки trait points коштує в редакторі видів (негативне = дає очки).
    return (
        # ══ ГОТОВІ RUN-ФАЙЛИ ═════════════════════════════════════════════════
        _v(run_command("pop_traits_353.txt"),      "★ Топ-5 трейтів (ID 353)",  "run pop_traits_353.txt — Psionic, Erudite, Robust, Fertile, Cybernetic одним файлом."),
        # ══ ОСНОВНІ БІОЛОГІЧНІ (04_species_traits) ══════════════════════════
        _v(_pop_add("trait_adaptive"),             "Adaptive",                  "cost=2. +20% Habitability на всіх планетах."),
        _v(_pop_add("trait_agrarian"),             "Agrarian",                  "cost=2. +15% Food від Farmers."),
        _v(_pop_add("trait_charismatic"),          "Charismatic",               "cost=2. +10% Happiness для інших видів поруч."),
        _v(_pop_add("trait_communal"),             "Communal",                  "cost=1. +5% Happiness."),
        _v(_pop_add("trait_conformists"),          "Conformists",               "cost=2. -15% Pop ethic divergence."),
        _v(_pop_add("trait_conservational"),       "Conservationist",           "cost=1. -10% Consumer Goods upkeep."),
        _v(_pop_add("trait_docile"),               "Docile",                    "cost=2. -10% Edict Cost."),
        _v(_pop_add("trait_enduring"),             "Enduring",                  "cost=1. +20 рр. Pop lifespan."),
        _v(_pop_add("trait_erudite"),              "Erudite",                   "cost=3. +10% Research speed. Конфліктує з Intelligent."),
        _v(_pop_add("trait_extremely_adaptive"),   "Extremely Adaptive",        "cost=4. +40% Habitability. Не стакати з Adaptive."),
        _v(_pop_add("trait_fertile"),              "Fertile",                   "cost=3. +Бонуси до розмноження (залежить від патчу)."),
        _v(_pop_add("trait_gene_mentorship"),      "Gene Mentorship",           "cost=2. +Бонуси для лідерів-вчених."),
        _v(_pop_add("trait_industrious"),          "Industrious",               "cost=2. +15% Minerals від Miners."),
        _v(_pop_add("trait_ingenious"),            "Ingenious",                 "cost=2. +10% Energy від Technicians."),
        _v(_pop_add("trait_intelligent"),          "Intelligent",               "cost=2. +5% Research speed."),
        _v(_pop_add("trait_natural_engineers"),    "Natural Engineers",         "cost=1. +15% Engineering Research."),
        _v(_pop_add("trait_natural_machinist"),    "Natural Machinist",         "cost=1. +10% output для Robot-виробничих робіт."),
        _v(_pop_add("trait_natural_physicists"),   "Natural Physicists",        "cost=1. +15% Physics Research."),
        _v(_pop_add("trait_natural_sociologists"), "Natural Sociologists",      "cost=1. +15% Society Research."),
        _v(_pop_add("trait_nomadic"),              "Nomadic",                   "cost=1. +10% Migration Speed."),
        _v(_pop_add("trait_quick_learners"),       "Quick Learners",            "cost=1. +25% Leader XP gain."),
        _v(_pop_add("trait_rapid_breeders"),       "Rapid Breeders",            "cost=2. +10% Pop Growth Speed."),
        _v(_pop_add("trait_resilient"),            "Resilient",                 "cost=1. +50% Army Health."),
        _v(_pop_add("trait_robust"),               "Robust",                    "cost=2. +20 рр. lifespan. Не конфліктує з Venerable."),
        _v(_pop_add("trait_sedentary"),            "Sedentary",                 "cost=-1. -10% Migration Speed."),  # негативний, але додати теж можна
        _v(_pop_add("trait_social_pheromones"),    "Social Pheromones",         "cost=1. Бонус Amenities/Happiness у колоніях."),
        _v(_pop_add("trait_strong"),               "Strong",                    "cost=1. +5% Army Damage, +5% Minerals."),
        _v(_pop_add("trait_talented"),             "Talented",                  "cost=1. +1 max Leader trait slot."),
        _v(_pop_add("trait_technical_skill"),      "Technical Skill",           "cost=1. +Output для технічних робіт (залежить від DLC)."),
        _v(_pop_add("trait_thrifty"),              "Thrifty",                   "cost=2. +15% Trade Value."),
        _v(_pop_add("trait_traditional"),          "Traditional",               "cost=1. +10% Unity."),
        _v(_pop_add("trait_uplifted"),             "Uplifted",                  "cost=0. Піднятий примітивний вид."),
        _v(_pop_add("trait_venerable"),            "Venerable",                 "cost=4. +80 рр. lifespan/leaders. Конфліктує з Fleeting/Short-Lived."),
        _v(_pop_add("trait_very_strong"),          "Very Strong",               "cost=3. +10% Army Damage, +10% Minerals. Не стакати зі Strong."),
        _v(_pop_add("trait_limited_regeneration"), "Limited Regeneration",      "cost=3. Регенерація армій у бою."),
        _v(_pop_add("trait_exotic_metabolism"),    "Exotic Metabolism",         "cost=1. Вид харчується рідкісними ресурсами."),
        _v(_pop_add("trait_repugnant"),            "Repugnant",                 "cost=-2. -10% Happiness інших видів поруч."),
        _v(_pop_add("trait_quarrelsome"),          "Quarrelsome",               "cost=-1. -10% Diplomatic weight."),
        _v(_pop_add("trait_deviants"),             "Deviants",                  "cost=-1. +20% Pop ethic divergence."),
        _v(_pop_add("trait_wasteful"),             "Wasteful",                  "cost=-1. +10% Consumer Goods upkeep."),
        _v(_pop_add("trait_weak"),                 "Weak",                      "cost=-1. -5% Army Damage, -5% Minerals."),
        _v(_pop_add("trait_slow_breeders"),        "Slow Breeders",             "cost=-2. -10% Pop Growth."),
        _v(_pop_add("trait_slow_learners"),        "Slow Learners",             "cost=-1. -25% Leader XP."),
        _v(_pop_add("trait_nonadaptive"),          "Non-Adaptive",              "cost=-2. -20% Habitability."),
        _v(_pop_add("trait_solitary"),             "Solitary",                  "cost=-1. -10% Happiness на перенаселених."),
        _v(_pop_add("trait_unruly"),               "Unruly",                    "cost=-2. +10% Edict Upkeep."),
        _v(_pop_add("trait_decadent"),             "Decadent",                  "cost=-1. -20% Productivity Entertainers."),
        _v(_pop_add("trait_fleeting"),             "Fleeting",                  "cost=-1. -20 рр. Leader lifespan."),
        _v(_pop_add("trait_fleeting_lithoid"),     "Fleeting (Lithoid)",        "cost=-1. -20 рр. lifespan для літоїдів."),
        # ══ ХАРАКТЕРИСТИКИ (02_basic_characteristics) ═══════════════════════
        _v(_pop_add("trait_organic"),              "Organic",                   "cost=0. Базовий органічний тип."),
        _v(_pop_add("trait_mechanical"),           "Mechanical",                "cost=0. Механічний тип. Не потребує їжі."),
        _v(_pop_add("trait_machine_unit"),         "Machine Unit",              "cost=0. Машинний юніт (Gestalt Machine)."),
        _v(_pop_add("trait_hive_mind"),            "Hive Mind",                 "cost=0. Вулик. Тільки для Hive-гештальтів."),
        _v(_pop_add("trait_lithoid"),              "Lithoid",                   "cost=0. Мінерали замість їжі, -50% Growth Speed."),
        _v(_pop_add("trait_syncretic_proles"),     "Syncretic Proles",          "cost=0. Робоча каста у Syncretic Evolution."),
        _v(_pop_add("trait_zombie"),               "Zombie",                    "cost=0. Зомбі (Necroids DLC)."),
        _v(_pop_add("trait_necrophage"),           "Necrophage",                "cost=0. Некрофаг: поглинає інші види."),
        _v(_pop_add("trait_void_dweller_1"),       "Void Dweller 1",            "cost=0. Перша стадія Void Dweller origin."),
        _v(_pop_add("trait_void_dweller_2"),       "Void Dweller 2",            "cost=0. Друга стадія Void Dweller origin."),
        _v(_pop_add("trait_clone_soldier_ascendant"), "Clone Soldier Ascendant","cost=0. Apex Clones — Engineered Evolution origin."),
        _v(_pop_add("trait_vat_grown"),            "Vat-Grown",                 "cost=0. Клонований вид."),
        _v(_pop_add("trait_self_modified"),        "Self-Modified",             "cost=0. Самостійно модифікований вид."),
        _v(_pop_add("trait_survivor"),             "Survivor",                  "cost=0. Вижив після ядерної зими."),
        _v(_pop_add("trait_marked"),               "Marked",                    "cost=0. Позначений Shroud."),
        _v(_pop_add("trait_invasive"),             "Invasive",                  "cost=0. Інвазивний вид."),
        _v(_pop_add("trait_noxious"),              "Noxious",                   "cost=1. Toxic God origin: отруйний, -Happiness іншим."),
        _v(_pop_add("trait_nerve_stapled"),        "Nerve-Stapled",             "cost=0. Без Happiness penalty. Для рабів."),
        _v(_pop_add("trait_enigmatic_intelligence"), "Enigmatic Intelligence",  "cost=0. +Research бонус (Enigmatic Fortress)."),
        _v(_pop_add("trait_enigmatic_intelligence_poor"), "Enigm. Intel. Poor", "cost=0. Провалений Enigmatic Intelligence."),
        # ══ ХАБІТАТ / ПРЕФЕРЕНЦІЇ (01_habitability) ═════════════════════════
        _v(_pop_add("trait_pc_alpine_preference"),           "Prefer: Alpine",          "cost=0. +25% Habitability на Alpine."),
        _v(_pop_add("trait_pc_arctic_preference"),           "Prefer: Arctic",          "cost=0. +25% на Arctic."),
        _v(_pop_add("trait_pc_arid_preference"),             "Prefer: Arid",            "cost=0. +25% на Arid."),
        _v(_pop_add("trait_pc_continental_preference"),      "Prefer: Continental",     "cost=0. +25% на Continental."),
        _v(_pop_add("trait_pc_desert_preference"),           "Prefer: Desert",          "cost=0. +25% на Desert."),
        _v(_pop_add("trait_pc_ocean_preference"),            "Prefer: Ocean",           "cost=0. +25% на Ocean."),
        _v(_pop_add("trait_pc_savannah_preference"),         "Prefer: Savannah",        "cost=0. +25% на Savannah."),
        _v(_pop_add("trait_pc_tropical_preference"),         "Prefer: Tropical",        "cost=0. +25% на Tropical."),
        _v(_pop_add("trait_pc_tundra_preference"),           "Prefer: Tundra",          "cost=0. +25% на Tundra."),
        _v(_pop_add("trait_pc_gaia_preference"),             "Prefer: Gaia",            "cost=1. Вважає Gaia рідною."),
        _v(_pop_add("trait_pc_gaia_preference_terraforming"), "Prefer: Gaia (Terraforming)", "cost=0. Terraform версія."),
        _v(_pop_add("trait_pc_nuked_preference"),            "Prefer: Tomb World",      "cost=0. +25% на Tomb World."),
        _v(_pop_add("trait_pc_habitat_preference"),          "Prefer: Habitat",         "cost=0. +25% на Habitats."),
        _v(_pop_add("trait_pc_ringworld_habitable_preference"), "Prefer: Ringworld",    "cost=0. +25% на Ring World."),
        _v(_pop_add("trait_pc_shattered_ring_habitable_preference"), "Prefer: Shattered Ring", "cost=0."),
        _v(_pop_add("trait_pc_hive_preference"),             "Prefer: Hive World",      "cost=0. +25% на Hive World."),
        _v(_pop_add("trait_pc_machine_preference"),          "Prefer: Machine World",   "cost=0. +25% на Machine World."),
        _v(_pop_add("trait_pc_relic_preference"),            "Prefer: Relic World",     "cost=0. +25% на Relic World."),
        _v(_pop_add("trait_pc_city_preference"),             "Prefer: Ecumenopolis",    "cost=0. +25% на Ecumenopolis."),
        _v(_pop_add("trait_pc_ai_preference"),               "Prefer: AI World",        "cost=0. Contingency AI preference."),
        _v(_pop_add("trait_pc_volcanic_preference"),         "Prefer: Volcanic",        "cost=0. +25% на Volcanic."),
        _v(_pop_add("trait_pc_ark_preference"),              "Prefer: Ark",             "cost=0. +25% на Ark."),
        _v(_pop_add("trait_pc_cosmogenesis_world_preference"), "Prefer: Synaptic Lathe","cost=0. +25% на Cosmogenesis."),
        _v(_pop_add("trait_wet_planet_preference"),          "Prefer: Wet planets",     "cost=0. Загальний мокрий тип."),
        _v(_pop_add("trait_dry_planet_preference"),          "Prefer: Dry planets",     "cost=0. Загальний сухий тип."),
        _v(_pop_add("trait_volcanic_planet_preference"),     "Prefer: Volcanic (gen.)", "cost=0. Загальний вулканічний."),
        _v(_pop_add("trait_machine_habitat_planet_preference"), "Machine: Habitat",     "cost=0. Machine unit habitat pref."),
        _v(_pop_add("trait_machine_pc_gaia_preference"),     "Machine: Prefer Gaia",    "cost=0."),
        _v(_pop_add("trait_machine_pc_machine_preference"),  "Machine: Prefer Machine", "cost=0."),
        _v(_pop_add("trait_machine_pc_nanotech_preference"), "Machine: Prefer Nanotech","cost=0."),
        _v(_pop_add("trait_machine_pc_nuked_preference"),    "Machine: Prefer Tomb",    "cost=0."),
        _v(_pop_add("trait_machine_pc_relic_preference"),    "Machine: Prefer Relic",   "cost=0."),
        _v(_pop_add("trait_machine_pc_ringworld_habitable_preference"), "Machine: Prefer Ring", "cost=0."),
        _v(_pop_add("trait_machine_pc_shattered_ring_habitable_preference"), "Machine: Prefer Shattered Ring", "cost=0."),
        # ══ ПРЕ-САПІЄНТИ (03_presapients) ═══════════════════════════════════
        _v(_pop_add("trait_presapient_stage"),               "Presapient Stage",        "cost=0. Базовий pre-sapient."),
        _v(_pop_add("trait_presapient_conservative"),        "Presapient: Conservative","cost=0."),
        _v(_pop_add("trait_presapient_docile_livestock"),    "Presapient: Livestock",   "cost=0."),
        _v(_pop_add("trait_presapient_earthbound"),          "Presapient: Earthbound",  "cost=0."),
        _v(_pop_add("trait_presapient_forcefully_devolved"), "Presapient: Devolved",    "cost=0."),
        _v(_pop_add("trait_presapient_irradiated"),          "Presapient: Irradiated",  "cost=0."),
        _v(_pop_add("trait_presapient_natural_intellectuals"), "Presapient: Intellectuals", "cost=0."),
        _v(_pop_add("trait_presapient_proles"),              "Presapient: Proles",      "cost=0."),
        _v(_pop_add("trait_presapient_starborn"),            "Presapient: Starborn",    "cost=0. Спейсборн pre-sapient."),
        _v(_pop_add("trait_presapient_unintelligent"),       "Presapient: Unintelligent","cost=0."),
        # ══ РОБОТИ (05_robotic) ══════════════════════════════════════════════
        _v(_pop_add("trait_robot_efficient_processors"),     "Robot: Efficient Processors",   "cost=2. +10% Research."),
        _v(_pop_add("trait_robot_logic_engines"),            "Robot: Logic Engines",          "cost=1. +5% Research Speed."),
        _v(_pop_add("trait_robot_enhanced_memory"),          "Robot: Enhanced Memory",        "cost=1. +10% Research."),
        _v(_pop_add("trait_robot_artificial_engineers"),     "Robot: Artificial Engineers",   "cost=1. +15% Engineering Research."),
        _v(_pop_add("trait_robot_artificial_physicists"),    "Robot: Artificial Physicists",  "cost=1. +15% Physics Research."),
        _v(_pop_add("trait_robot_artificial_sociologists"),  "Robot: Artificial Sociologists","cost=1. +15% Society Research."),
        _v(_pop_add("trait_robot_harvesters"),               "Robot: Harvesters",             "cost=1. +15% Minerals."),
        _v(_pop_add("trait_robot_power_drills"),             "Robot: Power Drills",           "cost=1. +10% Minerals."),
        _v(_pop_add("trait_robot_mote_powered_tools"),       "Robot: Mote Powered Tools",     "cost=2. +20% Minerals. Потрібні Volatile Motes."),
        _v(_pop_add("trait_robot_superconductive"),          "Robot: Superconductive",        "cost=1. +10% Energy."),
        _v(_pop_add("trait_robot_volatile_mote_reactor"),    "Robot: Volatile Mote Reactor",  "cost=2. +20% Energy. Потрібні Motes."),
        _v(_pop_add("trait_robot_rare_crystal_exterior"),    "Robot: Rare Crystal Exterior",  "cost=2. +20% Energy. Потрібні Crystals."),
        _v(_pop_add("trait_robot_domestic_protocols"),       "Robot: Domestic Protocols",     "cost=1. +10% Amenities."),
        _v(_pop_add("trait_robot_propaganda_machines"),      "Robot: Propaganda Machines",    "cost=1. +10% Unity."),
        _v(_pop_add("trait_robot_trading_algorithms"),       "Robot: Trading Algorithms",     "cost=1. +10% Trade Value."),
        _v(_pop_add("trait_robot_matrix_trading"),           "Robot: Matrix Trading",         "cost=2. +15% Trade Value."),
        _v(_pop_add("trait_robot_recycled"),                 "Robot: Recycled",               "cost=1. +10% Consumer Goods output."),
        _v(_pop_add("trait_robot_scarcity_algorithms"),      "Robot: Scarcity Algorithms",    "cost=2. -15% Consumer Goods upkeep."),
        _v(_pop_add("trait_robot_streamlined_protocols"),    "Robot: Streamlined Protocols",  "cost=1. -10% upkeep."),
        _v(_pop_add("trait_robot_repurposed_hardware"),      "Robot: Repurposed Hardware",    "cost=2. +Various від перепрофільованих компонентів."),
        _v(_pop_add("trait_robot_double_jointed"),           "Robot: Double-Jointed",         "cost=1. +10% Army Damage."),
        _v(_pop_add("trait_robot_integrated_weaponry"),      "Robot: Integrated Weaponry",    "cost=2. +Army Damage/Health."),
        _v(_pop_add("trait_robot_shielded_components"),      "Robot: Shielded Components",    "cost=2. +Army Health."),
        _v(_pop_add("trait_robot_custom_made"),              "Robot: Custom-Made",            "cost=1. +10% Happiness для господарів."),
        _v(_pop_add("trait_robot_loyalty_circuits"),         "Robot: Loyalty Circuits",       "cost=1. +10% Happiness."),
        _v(_pop_add("trait_robot_emotion_emulators"),        "Robot: Emotion Emulators",      "cost=1. +10% Happiness."),
        _v(_pop_add("trait_robot_learning_algorithms"),      "Robot: Learning Algorithms",    "cost=1. +25% Leader XP."),
        _v(_pop_add("trait_robot_inquisitative_axioms"),     "Robot: Inquisitative Axioms",   "cost=2. +Archaeology speed."),
        _v(_pop_add("trait_robot_durable"),                  "Robot: Durable",                "cost=1. +20% lifespan (менше деградації)."),
        _v(_pop_add("trait_robot_mass_produced"),            "Robot: Mass-Produced",          "cost=1. +25% Pop Assembly Speed."),
        _v(_pop_add("trait_robot_high_bandwidth"),           "Robot: High Bandwidth",         "cost=2. +1 Designations slot."),
        _v(_pop_add("trait_robot_ferro_viscosity_augmentation"), "Robot: Ferro Viscosity Aug.","cost=2. +Mining/Production."),
        _v(_pop_add("trait_robot_biomimetic_assembly"),      "Robot: Biomimetic Assembly",    "cost=2. Асемблює без спеціальних будівель."),
        _v(_pop_add("trait_robot_monoform"),                 "Robot: Monoform",               "cost=2. Усі роботи однакові — менше витрат."),
        _v(_pop_add("trait_robot_aquatic"),                  "Robot: Aquatic",                "cost=1. +Output на Ocean/Aquatic планетах."),
        _v(_pop_add("trait_robot_cave_dweller"),             "Robot: Cave Dweller",           "cost=1. +Output у підземних середовищах."),
        _v(_pop_add("trait_robot_survivor"),                 "Robot: Survivor",               "cost=1. +Output на Tomb/Nuked планетах."),
        _v(_pop_add("trait_robot_scavenger_bot"),            "Robot: Scavenger Bot",          "cost=2. +Ресурси від Debris/Wreckage."),
        _v(_pop_add("trait_robot_latent_psionic"),           "Robot: Latent Psionic",         "cost=0. Псіонічний потенціал (Machine Age DLC)."),
        _v(_pop_add("trait_robot_psionic"),                  "Robot: Psionic",                "cost=0. Псіонічний робот."),
        _v(_pop_add("trait_robot_digital_1"),                "Robot: Digital 1",              "cost=0. Перший ступінь цифровизації."),
        _v(_pop_add("trait_robot_digital_2"),                "Robot: Digital 2",              "cost=0. Другий ступінь цифровизації."),
        _v(_pop_add("trait_robot_notofthisworld"),           "Robot: Not of This World",      "cost=0. Alien machine trait."),
        _v(_pop_add("trait_robot_synthetic_dawn"),           "Robot: Synthetic Dawn",         "cost=0. Синтетичний схід."),
        _v(_pop_add("trait_robot_immortality"),              "Robot: Immortality",            "cost=0. Безсмертній машинний лідер."),
        _v(_pop_add("trait_robot_suppressed"),               "Robot: Suppressed",             "cost=0. Пригнічений робот."),
        _v(_pop_add("trait_robot_luxurious"),                "Robot: Luxurious",              "cost=1. +Amenities luxury."),
        _v(_pop_add("trait_robot_enigmatic_fortress"),       "Robot: Enigmatic Fortress",     "cost=2. Enigmatic Fortress reward trait."),
        _v(_pop_add("trait_robot_ancient_dreadnought"),      "Robot: Ancient Dreadnought",    "cost=2. Ancient Dreadnought reward."),
        _v(_pop_add("trait_robot_infinity_sphere"),          "Robot: Infinity Sphere",        "cost=2. Infinity Sphere reward."),
        _v(_pop_add("trait_robot_ceaseless_symmetric_annihilation_engine"), "Robot: CSAE",   "cost=2. Ceaseless Symmetric Annihilation Engine."),
        _v(_pop_add("trait_robot_history_artbot"),           "Robot: History Artbot",         "cost=0. Artbot historical trait."),
        _v(_pop_add("trait_robot_history_chatbot"),          "Robot: History Chatbot",        "cost=0."),
        _v(_pop_add("trait_robot_history_explorebot"),       "Robot: History Explorebot",     "cost=0."),
        _v(_pop_add("trait_robot_history_researchbot"),      "Robot: History Researchbot",    "cost=0."),
        _v(_pop_add("trait_robot_history_resourcebot"),      "Robot: History Resourcebot",    "cost=0."),
        _v(_pop_add("trait_robot_history_warbot"),           "Robot: History Warbot",         "cost=0."),
        # Негативні роботи
        _v(_pop_add("trait_robot_uncanny"),                  "Robot: Uncanny",                "cost=-1. -5% Happiness органіків поруч."),
        _v(_pop_add("trait_robot_bulky"),                    "Robot: Bulky",                  "cost=-1. +Housing usage."),
        _v(_pop_add("trait_robot_delicate_frames"),          "Robot: Delicate Frames",        "cost=-1. -10% Army Damage."),
        _v(_pop_add("trait_robot_high_maintenance"),         "Robot: High Maintenance",       "cost=-2. +Consumer Goods upkeep."),
        _v(_pop_add("trait_robot_exotic_fuel_consumption"),  "Robot: Exotic Fuel",            "cost=-2. Потребує рідкісних ресурсів."),
        _v(_pop_add("trait_robot_quarrelsome"),              "Robot: Quarrelsome",            "cost=-1. -Diplomatic weight."),
        _v(_pop_add("trait_robot_deviants"),                 "Robot: Deviants",               "cost=-1. +Ethic divergence."),
        _v(_pop_add("trait_robot_decadent"),                 "Robot: Decadent",               "cost=-1. -Entertainer productivity."),
        _v(_pop_add("trait_robot_wasteful"),                 "Robot: Wasteful",               "cost=-1. +Consumer Goods upkeep."),
        _v(_pop_add("trait_robot_assembly_slag"),            "Robot: Assembly Slag",          "cost=2 (Infernals). +Output від шлаку."),
        # ══ ВОЗНЕСІННЯ (09_ascension) ════════════════════════════════════════
        _v(_pop_add("trait_latent_psionic"),                 "Latent Psionic",               "cost=0. Передумова для Psionic AP."),
        _v(_pop_add("trait_psionic"),                        "Psionic",                      "cost=0. +Research/Happiness/Unity, доступ до Shroud."),
        _v(_pop_add("trait_elevated_synapses"),              "Elevated Synapses",            "cost=0. Machine Age нейро-вознесіння."),
        _v(_pop_add("trait_cybernetic"),                     "Cybernetic",                   "cost=0. +10% Minerals, +5% Army, +10% Habitability."),
        _v(_pop_add("trait_synthetic"),                      "Synthetic",                    "cost=0. Синтетичний вид (Synthetic Evolution)."),
        _v(_pop_add("trait_perfected_genes"),                "Perfected Genes",              "cost=0. Genetic Ascension: максимально покращені гени."),
        _v(_pop_add("trait_spliced_adaptability"),           "Spliced Adaptability",         "cost=1. Toxic God DLC: +Habitability splicing."),
        _v(_pop_add("trait_expressed_tradition"),            "Expressed Tradition",          "cost=0. Genetic tradition expression trait."),
        # ══ DISTANT STARS (06) ══════════════════════════════════════════════
        _v(_pop_add("trait_tiyanki"),                        "Tiyanki",                      "cost=0. Tiyanki pre-sapient."),
        _v(_pop_add("trait_voidling"),                       "Voidling",                     "cost=0. Voidling pre-sapient."),
        _v(_pop_add("trait_nivlac"),                         "Nivlac",                       "cost=0. Nivlac pre-sapient."),
        _v(_pop_add("trait_notofthisworld"),                 "Not of This World",            "cost=0. Alien origin trait."),
        _v(_pop_add("trait_delicious"),                      "Delicious",                    "cost=0. Смачний вид (Tiyanki interaction)."),
        # ══ MEGACORP (07) ════════════════════════════════════════════════════
        _v(_pop_add("trait_nuumismatic_administration"),     "Numismatic Administration",    "cost=1. +Trade Value від адміністраторів."),
        # ══ ANCIENT RELICS (08) ══════════════════════════════════════════════
        _v(_pop_add("trait_drake_scaled"),                   "Drake-Scaled",                 "cost=1. +Army Health, +5% Habitability. Drake reward."),
        _v(_pop_add("trait_ductile"),                        "Ductile",                      "cost=1. Nanite trait (L-Cluster)."),
        _v(_pop_add("trait_excessive_endurance"),            "Excessive Endurance",          "cost=2. +Soldier/Army бонуси."),
        _v(_pop_add("trait_felsic"),                         "Felsic",                       "cost=1. Lithoid special reward trait."),
        _v(_pop_add("trait_haunting_visions"),               "Haunting Visions",             "cost=-2. (Shroud) -Happiness, але +Psionic."),
        _v(_pop_add("trait_juiced_power"),                   "Juiced Power",                 "cost=1. (Toxic God DLC) +Output."),
        _v(_pop_add("trait_low_maintenance"),                "Low Maintenance",              "cost=1. -Maintenance Cost."),
        _v(_pop_add("trait_preplanned_growth"),              "Preplanned Growth",            "cost=2. Controlled pop growth (Toxic God)."),
        # ══ LITHOID (04, базові) ═════════════════════════════════════════════
        _v(_pop_add("trait_lithoid_budding"),                "Lithoid Budding",              "cost=2. +Pop Growth через брунькування."),
        _v(_pop_add("trait_lithoid_gaseous_byproducts"),     "Lithoid Gaseous Byproducts",   "cost=1. +Exotic Gases output."),
        _v(_pop_add("trait_lithoid_scintillating"),          "Lithoid Scintillating",        "cost=1. +Rare Crystals output."),
        _v(_pop_add("trait_lithoid_volatile_excretions"),    "Lithoid Volatile Excretions",  "cost=1. +Volatile Motes output."),
        _v(_pop_add("trait_rapid_breeders_lithoid"),         "Rapid Breeders (Lithoid)",     "cost=2. +Lithoid growth speed."),
        # ══ PLANTOID / FUNGOID спеціальні ════════════════════════════════════
        _v(_pop_add("trait_plantoid_bloomed"),               "Plantoid Bloomed",             "cost=2. +Growth/Output для Plantoid."),
        _v(_pop_add("trait_plantoid_budding"),               "Plantoid Budding",             "cost=2. +Pop Growth через брунькування."),
        _v(_pop_add("trait_plantoid_phototrophic"),          "Plantoid Phototrophic",        "cost=1. Енергія від сонця замість їжі."),
        _v(_pop_add("trait_plantoid_radiotrophic"),          "Plantoid Radiotrophic",        "cost=2. Енергія від радіації."),
        # ══ ТІЛО / БІОЛОГІЯ ══════════════════════════════════════════════════
        _v(_pop_add("trait_aquatic"),                        "Aquatic",                      "cost=1. +Output на Ocean/Aquatic. DLC Aquatics."),
        _v(_pop_add("trait_incubator"),                      "Incubator",                    "cost=2. +Pop Growth Speed (Hive)."),
        _v(_pop_add("trait_farm_hands"),                     "Farm Hands",                   "cost=1. +Food від Farmers."),
        _v(_pop_add("trait_egg_laying"),                     "Egg-Laying",                   "cost=2. +Pop Growth rate (Biogenesis DLC)."),
        _v(_pop_add("trait_familial"),                       "Familial",                     "cost=2. Сімейні бонуси до Growth/Happiness."),
        _v(_pop_add("trait_flight"),                         "Flight",                       "cost=2. +Army Damage, +Migration Speed."),
        _v(_pop_add("trait_shelled"),                        "Shelled",                      "cost=3. +Army Health/Defence."),
        _v(_pop_add("trait_spare_organs"),                   "Spare Organs",                 "cost=2. +Lifespan, +Army Health."),
        _v(_pop_add("trait_seasonal_dormancy"),              "Seasonal Dormancy",            "cost=2. Fluctuating output/upkeep."),
        _v(_pop_add("trait_camouflage"),                     "Camouflage",                   "cost=1. +Army Evasion/Stealth."),
        _v(_pop_add("trait_genetic_memory"),                 "Genetic Memory",               "cost=3. +Leader XP, +Research."),
        _v(_pop_add("trait_acidic_vascularity"),             "Acidic Vascularity",           "cost=1. +Army Damage через acid."),
        _v(_pop_add("trait_hollow_bones"),                   "Hollow Bones",                 "cost=-3. -Army Health, але +Migration."),
        _v(_pop_add("trait_rooted"),                         "Rooted",                       "cost=-3. -Migration Speed, +Stability."),
        _v(_pop_add("trait_brittle"),                        "Brittle",                      "cost=-3. -Army/Pop Health."),
        _v(_pop_add("trait_permeable_skin"),                 "Permeable Skin",               "cost=-1. +Vulnerability до атак."),
        _v(_pop_add("trait_nascent_stage"),                  "Nascent Stage",                "cost=-2. Молодий вид з обмеженнями."),
        _v(_pop_add("trait_wilderness"),                     "Wilderness",                   "cost=0. Pre-uplift дикий вид."),
        # ══ CYBORG (10) ══════════════════════════════════════════════════════
        _v(_pop_add("trait_auto_mod_cyborg"),                "Auto-Mod Cyborg",              "cost=2. Автоматично оновлює кіборг-трейти."),
        _v(_pop_add("trait_cyborg_efficient_processors"),    "Cyborg: Efficient Processors", "cost=2. +10% Research."),
        _v(_pop_add("trait_cyborg_logic_engines"),           "Cyborg: Logic Engines",        "cost=1. +5% Research."),
        _v(_pop_add("trait_cyborg_enhanced_memory"),         "Cyborg: Enhanced Memory",      "cost=1. +10% Research."),
        _v(_pop_add("trait_cyborg_bionic_engineers"),        "Cyborg: Bionic Engineers",     "cost=1. +15% Engineering."),
        _v(_pop_add("trait_cyborg_bionic_physicists"),       "Cyborg: Bionic Physicists",    "cost=1. +15% Physics."),
        _v(_pop_add("trait_cyborg_bionic_sociologists"),     "Cyborg: Bionic Sociologists",  "cost=1. +15% Society."),
        _v(_pop_add("trait_cyborg_harvesters"),              "Cyborg: Harvesters",           "cost=1. +15% Minerals."),
        _v(_pop_add("trait_cyborg_power_drills"),            "Cyborg: Power Drills",         "cost=1. +10% Minerals."),
        _v(_pop_add("trait_cyborg_superconductive"),         "Cyborg: Superconductive",      "cost=1. +10% Energy."),
        _v(_pop_add("trait_cyborg_propaganda_machines"),     "Cyborg: Propaganda Machines",  "cost=1. +10% Unity."),
        _v(_pop_add("trait_cyborg_trading_algorithms"),      "Cyborg: Trading Algorithms",   "cost=1. +10% Trade Value."),
        _v(_pop_add("trait_cyborg_streamlined_protocols"),   "Cyborg: Streamlined Protocols","cost=1. -10% upkeep."),
        _v(_pop_add("trait_cyborg_scarcity_algorithms"),     "Cyborg: Scarcity Algorithms",  "cost=-1. -Consumer Goods penalty."),
        _v(_pop_add("trait_cyborg_learning_algorithms"),     "Cyborg: Learning Algorithms",  "cost=1. +25% Leader XP."),
        _v(_pop_add("trait_cyborg_double_jointed"),          "Cyborg: Double-Jointed",       "cost=1. +Army Damage."),
        _v(_pop_add("trait_cyborg_integrated_weaponry"),     "Cyborg: Integrated Weaponry",  "cost=1. +Army Damage/Health."),
        _v(_pop_add("trait_cyborg_durable"),                 "Cyborg: Durable",              "cost=1. +Lifespan."),
        _v(_pop_add("trait_cyborg_mass_produced"),           "Cyborg: Mass-Produced",        "cost=1. +Pop Assembly."),
        _v(_pop_add("trait_cyborg_loyalty_circuits"),        "Cyborg: Loyalty Circuits",     "cost=1. +Happiness."),
        _v(_pop_add("trait_cyborg_stainless_steel_smile"),   "Cyborg: Stainless Steel Smile","cost=1. +Diplomacy/Happiness інших."),
        _v(_pop_add("trait_cyborg_scavenger_bot"),           "Cyborg: Scavenger Bot",        "cost=2. +Debris/Wreckage ресурси."),
        _v(_pop_add("trait_cyborg_enigmatic_fortress"),      "Cyborg: Enigmatic Fortress",   "cost=2. Enigmatic Fortress reward."),
        _v(_pop_add("trait_cyborg_ancient_dreadnought"),     "Cyborg: Ancient Dreadnought",  "cost=2. Ancient Dreadnought reward."),
        _v(_pop_add("trait_cyborg_infinity_sphere"),         "Cyborg: Infinity Sphere",      "cost=2. Infinity Sphere reward."),
        _v(_pop_add("trait_cyborg_climate_adjustment_cold"), "Cyborg: Cold Adjustment",      "cost=1. +Habitability cold planets."),
        _v(_pop_add("trait_cyborg_climate_adjustment_dry"),  "Cyborg: Dry Adjustment",       "cost=1. +Habitability dry planets."),
        _v(_pop_add("trait_cyborg_climate_adjustment_wet"),  "Cyborg: Wet Adjustment",       "cost=1. +Habitability wet planets."),
        _v(_pop_add("trait_cyborg_creed_of_construction"),   "Cyborg: Creed of Construction","cost=0. Ідеологія кіборгів-будівельників."),
        _v(_pop_add("trait_cyborg_creed_of_labor"),          "Cyborg: Creed of Labor",       "cost=0. Ідеологія кіборгів-робітників."),
        _v(_pop_add("trait_cyborg_creed_of_research"),       "Cyborg: Creed of Research",    "cost=0. Ідеологія кіборгів-вчених."),
        _v(_pop_add("trait_cyborg_creed_of_war"),            "Cyborg: Creed of War",         "cost=0. Ідеологія кіборгів-вояків."),
        _v(_pop_add("trait_cyborg_ritualistic_implants"),    "Cyborg: Ritualistic Implants", "cost=0. Ритуальні імпланти."),
        _v(_pop_add("trait_cyborg_welded_countenance"),      "Cyborg: Welded Countenance",   "cost=-2. -Diplomacy/Happiness інших."),
        _v(_pop_add("trait_cyborg_bulky"),                   "Cyborg: Bulky",                "cost=-2. +Housing usage."),
        _v(_pop_add("trait_cyborg_delicate_frames"),         "Cyborg: Delicate Frames",      "cost=-1. -Army Damage."),
        _v(_pop_add("trait_cyborg_high_maintenance"),        "Cyborg: High Maintenance",     "cost=-2. +Upkeep."),
        _v(_pop_add("trait_cyborg_high_bandwidth"),          "Cyborg: High Bandwidth",       "cost=-2. Bandwidth penalty."),
        _v(_pop_add("trait_cyborg_neural_limiters"),         "Cyborg: Neural Limiters",      "cost=-2. -Research."),
        _v(_pop_add("trait_cyborg_limited_memory"),          "Cyborg: Limited Memory",       "cost=-2. -Leader XP."),
        _v(_pop_add("trait_cyborg_power_intensive"),         "Cyborg: Power Intensive",      "cost=-1. +Energy upkeep."),
        _v(_pop_add("trait_cyborg_apathy_loops"),            "Cyborg: Apathy Loops",         "cost=-1. -Happiness."),
        # ══ MACHINE AGE / UNPLUGGED (13, 15) ═════════════════════════════════
        _v(_pop_add("trait_limited_cybernetic"),             "Limited Cybernetic",           "cost=0. Machine Age: часткова кіборгізація."),
        _v(_pop_add("trait_pathogenic_genes"),               "Pathogenic Genes",             "cost=-1. Machine Age: -Output від хвороби."),
        _v(_pop_add("trait_unplugged_cybernetic_positives_1"), "Unplugged: Cyber+ 1",        "cost=0. Позитивний кіберімплант (Unplugged)."),
        _v(_pop_add("trait_unplugged_cybernetic_positives_2"), "Unplugged: Cyber+ 2",        "cost=0."),
        _v(_pop_add("trait_unplugged_cybernetic_positives_3"), "Unplugged: Cyber+ 3",        "cost=0."),
        _v(_pop_add("trait_unplugged_cybernetic_negatives_1"), "Unplugged: Cyber− 1",        "cost=0. Негативний кіберімплант."),
        _v(_pop_add("trait_unplugged_cybernetic_negatives_2"), "Unplugged: Cyber− 2",        "cost=0."),
        _v(_pop_add("trait_unplugged_cybernetic_negatives_3"), "Unplugged: Cyber− 3",        "cost=0."),
        _v(_pop_add("trait_unplugged_decyberized"),          "Unplugged: Decyberized",       "cost=0. Повністю знято кібернетику."),
        _v(_pop_add("trait_unplugged_neurocalmed"),          "Unplugged: Neurocalmed",       "cost=0. Нейрозаспокоєний."),
        _v(_pop_add("trait_unplugged_neurosavant"),          "Unplugged: Neurosavant",       "cost=0. Нейрогеній."),
        _v(_pop_add("trait_unplugged_regenoptimized"),       "Unplugged: Regen Optimized",   "cost=0. Оптимізована регенерація."),
        # ══ BIOGENESIS (15) ══════════════════════════════════════════════════
        _v(_pop_add("trait_malleable_genes"),                "Malleable Genes",              "cost=6. Biogenesis: максимальна гнучкість генів."),
        _v(_pop_add("trait_malleable_minerals"),             "Malleable: Minerals",          "cost=0. Biogenesis malleable mineral output."),
        _v(_pop_add("trait_malleable_energy"),               "Malleable: Energy",            "cost=0."),
        _v(_pop_add("trait_malleable_food"),                 "Malleable: Food",              "cost=0."),
        _v(_pop_add("trait_malleable_forge"),                "Malleable: Forge",             "cost=0."),
        _v(_pop_add("trait_malleable_research"),             "Malleable: Research",          "cost=0."),
        _v(_pop_add("trait_malleable_trade"),                "Malleable: Trade",             "cost=0."),
        _v(_pop_add("trait_malleable_unity"),                "Malleable: Unity",             "cost=0."),
        _v(_pop_add("trait_malleable_ameneties"),            "Malleable: Amenities",         "cost=0."),
        _v(_pop_add("trait_adaptive_mutations"),             "Adaptive Mutations",           "cost=0. Biogenesis: адаптивні мутації."),
        _v(_pop_add("trait_adaptive_minerals"),              "Adaptive: Minerals",           "cost=0."),
        _v(_pop_add("trait_adaptive_energy"),                "Adaptive: Energy",             "cost=0."),
        _v(_pop_add("trait_adaptive_food"),                  "Adaptive: Food",               "cost=0."),
        _v(_pop_add("trait_adaptive_forge"),                 "Adaptive: Forge",              "cost=0."),
        _v(_pop_add("trait_adaptive_research"),              "Adaptive: Research",           "cost=0."),
        _v(_pop_add("trait_adaptive_trade"),                 "Adaptive: Trade",              "cost=0."),
        _v(_pop_add("trait_adaptive_unity"),                 "Adaptive: Unity",              "cost=0."),
        _v(_pop_add("trait_adaptive_amenities"),             "Adaptive: Amenities",          "cost=0."),
        _v(_pop_add("trait_chromalogs"),                     "Chromalogs",                   "cost=4. Biogenesis: хромалоги — +різноманітні бонуси."),
        _v(_pop_add("trait_spatial_mastery"),                "Spatial Mastery",              "cost=4. Biogenesis: +Habitat/Orbital output."),
        _v(_pop_add("trait_structural_awareness"),           "Structural Awareness",         "cost=1. (Nomads) +Building/District output."),
        # ══ SHROUD / STRANGE WORLDS (17, 15_strange) ═════════════════════════
        _v(_pop_add("trait_cranial_hypertrophy"),            "Cranial Hypertrophy",          "cost=2. Shroud: +Psionic потужність."),
        _v(_pop_add("trait_cranial_megatrophy"),             "Cranial Megatrophy",           "cost=4. Shroud: максимальна псі-потужність."),
        _v(_pop_add("trait_uncanny_intuition"),              "Uncanny Intuition",            "cost=3. Shroud: +Research/Happiness."),
        _v(_pop_add("trait_tankbound"),                      "Tankbound",                    "cost=3. Shroud: фізична немічність, але +Psionic."),
        _v(_pop_add("trait_psionic_ephapse"),                "Psionic Ephapse",              "cost=?. Strange Worlds: псіонічний синапс."),
        _v(_pop_add("trait_geleboric_mutations"),            "Geleboric Mutations",          "cost=?. Strange Worlds: мутації Gelebor."),
        _v(_pop_add("trait_inner_darkness"),                 "Inner Darkness",               "cost=?. Strange Worlds: темрява всередині."),
        _v(_pop_add("trait_shroud_forged"),                  "Shroud-Forged",                "cost=0. Shroud: виготовлений у Shroud."),
        # ══ INFERNALS (16) ═══════════════════════════════════════════════════
        _v(_pop_add("trait_infernal"),                       "Infernal",                     "cost=0. Infernals DLC: пекельний вид."),
        _v(_pop_add("trait_pyroclastic"),                    "Pyroclastic",                  "cost=1. Infernals: вулканічні бонуси."),
        _v(_pop_add("trait_shell_slag"),                     "Shell Slag",                   "cost=2. Infernals: шлакова оболонка."),
        _v(_pop_add("trait_unbreakable_resolve"),            "Unbreakable Resolve",          "cost=2. Infernals: +Morale/Stability."),
        _v(_pop_add("trait_crucible_community"),             "Crucible Community",           "cost=1. Infernals: +Community bonuses."),
        # ══ NOMADS (18) ══════════════════════════════════════════════════════
        _v(_pop_add("trait_interconnected"),                 "Interconnected",               "cost=2. Nomads: +Synergy bonuses."),
        _v(_pop_add("trait_photoadaptive"),                  "Photoadaptive",                "cost=2. Nomads: +Output в залежності від зірки."),
        _v(_pop_add("trait_solar_cells"),                    "Solar Cells",                  "cost=2. Nomads: +Energy від зірки."),
        _v(_pop_add("trait_defence_drones"),                 "Defence Drones",               "cost=1. Nomads: +Army/Defence."),
        _v(_pop_add("trait_reavers"),                        "Reavers",                      "cost=2. Nomads: +Raiding/Combat."),
        _v(_pop_add("trait_recursive_learners"),             "Recursive Learners",           "cost=1. Nomads: +XP/Research."),
        _v(_pop_add("trait_terraphobic"),                    "Terraphobic",                  "cost=-1. Nomads: -Output на звичайних планетах."),
        # ══ MISC / EVENT TRAITS ══════════════════════════════════════════════
        _v(_pop_add("trait_inorganic_breath"),               "Inorganic Breath",             "cost=1. Дихає неорганічними речовинами."),
        _v(_pop_add("trait_exd"),                            "Exd",                          "cost=0. Astral Planes: невідомий trait."),
        _v(_pop_add("trait_plasmic"),                        "Plasmic",                      "cost=0. Astral Planes: плазмовий вид."),
        _v(_pop_add("trait_drone_collective"),               "Drone Collective",             "cost=0. Gestalt Drone variant."),
        # ══ REMOVE НЕГАТИВНИХ ════════════════════════════════════════════════
        _v(_pop_remove("trait_nonadaptive"),                 "↩ Non-Adaptive",              "-20% Habitability → ЗНІМАЄМО."),
        _v(_pop_remove("trait_repugnant"),                   "↩ Repugnant",                 "-10% Happiness інших → ЗНІМАЄМО."),
        _v(_pop_remove("trait_solitary"),                    "↩ Solitary",                  "-10% Happiness перенаселення → ЗНІМАЄМО."),
        _v(_pop_remove("trait_unruly"),                      "↩ Unruly",                    "+10% Edict Upkeep → ЗНІМАЄМО."),
        _v(_pop_remove("trait_decadent"),                    "↩ Decadent",                  "-20% Entertainers → ЗНІМАЄМО."),
        _v(_pop_remove("trait_slow_learners"),               "↩ Slow Learners",             "-25% Leader XP → ЗНІМАЄМО."),
        _v(_pop_remove("trait_fleeting"),                    "↩ Fleeting",                  "-20 рр. lifespan → ЗНІМАЄМО."),
        _v(_pop_remove("trait_fleeting_lithoid"),            "↩ Fleeting Lithoid",          "-20 рр. lifespan → ЗНІМАЄМО."),
        _v(_pop_remove("trait_short_lived"),                 "↩ Short-Lived",               "-40 рр. lifespan → ЗНІМАЄМО."),
        _v(_pop_remove("trait_weak"),                        "↩ Weak",                      "-5% Damage/-5% Minerals → ЗНІМАЄМО."),
        _v(_pop_remove("trait_quarrelsome"),                 "↩ Quarrelsome",               "-10% Diplomatic weight → ЗНІМАЄМО."),
        _v(_pop_remove("trait_deviants"),                    "↩ Deviants",                  "+20% ethic divergence → ЗНІМАЄМО."),
        _v(_pop_remove("trait_wasteful"),                    "↩ Wasteful",                  "+10% CG upkeep → ЗНІМАЄМО."),
        _v(_pop_remove("trait_sedentary"),                   "↩ Sedentary",                 "-10% Migration → ЗНІМАЄМО."),
        _v(_pop_remove("trait_slow_breeders"),               "↩ Slow Breeders",             "-10% Pop Growth → ЗНІМАЄМО."),
        _v(_pop_remove("trait_hollow_bones"),                "↩ Hollow Bones",              "-Army Health → ЗНІМАЄМО."),
        _v(_pop_remove("trait_rooted"),                      "↩ Rooted",                    "-Migration → ЗНІМАЄМО."),
        _v(_pop_remove("trait_brittle"),                     "↩ Brittle",                   "-Army Health → ЗНІМАЄМО."),
        _v(_pop_remove("trait_permeable_skin"),              "↩ Permeable Skin",            "+Vulnerability → ЗНІМАЄМО."),
        _v(_pop_remove("trait_nascent_stage"),               "↩ Nascent Stage",             "Обмеження молодого виду → ЗНІМАЄМО."),
        _v(_pop_remove("trait_terraphobic"),                 "↩ Terraphobic",               "-Output на планетах → ЗНІМАЄМО."),
        _v(_pop_remove("trait_haunting_visions"),            "↩ Haunting Visions",          "-Happiness (Shroud) → ЗНІМАЄМО."),
        _v(_pop_remove("trait_pathogenic_genes"),            "↩ Pathogenic Genes",          "-Output хвороба → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_uncanny"),               "↩ Robot: Uncanny",            "-5% Happiness органіків → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_bulky"),                 "↩ Robot: Bulky",              "+Housing → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_delicate_frames"),       "↩ Robot: Delicate Frames",    "-Army Damage → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_high_maintenance"),      "↩ Robot: High Maintenance",   "+Upkeep → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_exotic_fuel_consumption"), "↩ Robot: Exotic Fuel",      "+Exotic upkeep → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_quarrelsome"),           "↩ Robot: Quarrelsome",        "-Diplomatic → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_deviants"),              "↩ Robot: Deviants",           "+Divergence → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_decadent"),              "↩ Robot: Decadent",           "-Entertainers → ЗНІМАЄМО."),
        _v(_pop_remove("trait_robot_wasteful"),              "↩ Robot: Wasteful",           "+CG upkeep → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_welded_countenance"),   "↩ Cyborg: Welded Countenance","-Diplomacy → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_bulky"),                "↩ Cyborg: Bulky",             "+Housing → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_delicate_frames"),      "↩ Cyborg: Delicate Frames",   "-Army → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_high_maintenance"),     "↩ Cyborg: High Maintenance",  "+Upkeep → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_neural_limiters"),      "↩ Cyborg: Neural Limiters",   "-Research → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_limited_memory"),       "↩ Cyborg: Limited Memory",    "-Leader XP → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_power_intensive"),      "↩ Cyborg: Power Intensive",   "+Energy cost → ЗНІМАЄМО."),
        _v(_pop_remove("trait_cyborg_apathy_loops"),         "↩ Cyborg: Apathy Loops",      "-Happiness → ЗНІМАЄМО."),
    )


def _specific_tech_variants() -> tuple[Cheat, ...]:
    return (
        _v(run_command("tech_insights.txt"), "Pre-FTL Insights", "13 insight techs (Observation)."),
        _v(run_command("tech_precursors.txt"), "Precursor", "tech_secrets_* усіх ванільних ланцюгів."),
        _v(run_command("tech_archaeotech.txt"), "Archaeotech", "Archaeo зброя, броня, будівлі."),
        _v(run_command("tech_guardians.txt"), "Guardians", "Dragonscales, Enigmatic, Scavenger nanites."),
        _v(run_command("tech_space_fauna.txt"), "Space Fauna", "Amoeba/Tiyanki/crystal/voidworm. Фауну не вбиває."),
        _v(run_command("tech_fallen_empire.txt"), "Fallen Empire", "Dark Matter + FE будівлі."),
        _v(run_command("tech_crisis.txt"), "Crisis", "Unbidden/Prethoryn/Cetana. Кризу не запускає."),
        _v(run_command("tech_lcluster.txt"), "L-Cluster / Nanite", "Transmutation + neuroregen. L-Gate не відкриває."),
        _v(run_command("tech_astral.txt"), "Astral", "Rift Sphere. Ріфти не завершує."),
        _v(run_command("tech_events_unique.txt"), "Anomaly / event", "Curator, Caravan, Skrand, Extreme Frontiers."),
        _v(run_command("tech_rare_resources.txt"), "Рідкісні ресурси", "Living Metal / Zro / Dark Matter / Astral Harvesting."),
        _v(run_command("tech_psionic_event.txt"), "Psionic event", "Щити, зброя, psi jump. Без AP і covenant."),
    )


SPECIAL_WINDOW_CHEATS: tuple[Cheat, ...] = (
    Cheat(
        run_command("gaia78_capital_planet.txt"),
        "1. Гея 78",
        "Вибери колонізовану планету. Gaia 78, по 3 кожної фічі generator/mining/farming з меню. Без underground/спецдепозитів і без примусових районів. Без попів.",
        "Світи 78",
    ),
    Cheat(
        run_command("ecu78_capital_planet.txt"),
        "2. Екуменополіс 78",
        "Вибери колонізовану планету. pc_city, розмір 78. По 70 housing/urban_1/2/3 (ignore_cap). Без попів.",
        "Світи 78",
    ),
    Cheat(
        run_command("tech_all_specific.txt"),
        "3. Усі специфічні технології",
        "Insights + precursor/archaeotech/guardians/fauna/FE/crisis/L-Cluster/astral/event. Без вознесіння, Cosmogenesis, covenant, відкриття L-Gate. Клік копіює все; стрілка — окремі пакети.",
        "Наука",
        _specific_tech_variants(),
    ),
    Cheat(
        run_command("orbital_resources_300.txt"),
        "4. Орбітальні депозити",
        "Те саме, що Run · Орбітальні депозити в базовому віджеті. Вибери неживе тіло. Mining і research на одному тілі не мішай.",
        "Орбіта",
        (
            _v(
                run_command("orbital_resources_300.txt"),
                "Mining 300",
                "Нежива планета / астероїд / зірка. Energy, minerals, alloys, food, consumer goods по 300. Далі mining station.",
            ),
            _v(
                run_command("orbital_resources_3000.txt"),
                "Mining 3000",
                "Нежива планета / астероїд / зірка. Energy, minerals, alloys, food, consumer goods по 3000. Далі mining station.",
            ),
            _v(
                run_command("orbital_energy_10000.txt"),
                "Енергія 10000",
                "Нежива планета / астероїд / зірка. Energy ×10000 (10×100 d_energy_10). Далі mining station.",
            ),
            _v(
                run_command("orbital_energy_100000.txt"),
                "Енергія 100000",
                "Нежива планета / астероїд / зірка. Energy ×100000. Далі mining station.",
            ),
            _v(
                run_command("orbital_science_500.txt"),
                "Science 500×3",
                "Нежива планета / астероїд / зірка без mining-депозитів. Physics/Society/Engineering по 500. Далі research station.",
            ),
            _v(
                run_command("orbital_science_5000.txt"),
                "Science 5000×3",
                "Нежива планета / астероїд / зірка без mining-депозитів. Physics/Society/Engineering по 5000. Далі research station.",
            ),
            _v(
                run_command("orbital_special_mining_100.txt"),
                "Спец. mining 100",
                "Нежива планета без research-депозитів. Гази, кристали, motes, living metal, артефакти, trade.",
            ),
            _v(
                run_command("orbital_special_mining_1000.txt"),
                "Спец. mining 1000",
                "Нежива планета без research-депозитів. Гази, кристали, motes, living metal, артефакти, trade ×1000.",
            ),
            _v(
                run_command("orbital_special_research_100.txt"),
                "Спец. research 100",
                "Нежива планета без mining-депозитів. Dark matter, zro, nanites, astral, artifacts research, unity ×300.",
            ),
            _v(
                run_command("orbital_special_research_1000.txt"),
                "Спец. research 1000",
                "Нежива планета без mining-депозитів. Dark matter, zro, nanites, astral, artifacts research ×1000, unity ×3000.",
            ),
        ),
    ),
    Cheat(
        _pop_add("trait_intelligent"),
        "5. Трейти попів",
        (
            "debugtooltip → навести на планету або поп-групу → взяти ID. "
            "Замінити POP_GROUP_ID і назву трейту. "
            "Клік копіює шаблон з trait_intelligent; стрілка — всі трейти."
        ),
        "Світи 78",
        _pop_trait_variants(),
    ),
)


def _run_file_cheats() -> tuple[Cheat, ...]:
    items: list[Cheat] = []
    for script in RUN_SCRIPTS:
        if script.filename == "orbital_special_resources_100.txt":
            continue
        items.append(
            Cheat(
                run_command(script.filename),
                script.title,
                f"Виділи: {script.select}. {script.creates}",
                f"Run · {script.group}",
            )
        )
    return tuple(items)


CHEATS: tuple[Cheat, ...] = _run_file_cheats() + (
    Cheat(
        "`  або  Shift+Alt+C",
        "Відкрити консоль",
        "У звичайній (не Ironman) грі відкриває консоль. На частині клавіатур це ~, ^, § або °.",
        "Консоль",
    ),
    Cheat("help", "Список команд", "Показує всі доступні команди консолі.", "Консоль"),
    Cheat("help [команда]", "Довідка по команді", "Пояснює конкретну команду, наприклад: help cash", "Консоль"),
    Cheat(
        "debugtooltip",
        "ID під курсором",
        "Увімкнути підказки з ID планет, імперій, лідерів і кораблів. Потрібні для багатьох читів. Повтор вимикає.",
        "Консоль",
    ),
    Cheat("cash 5000", "Енергія", "Додає енергокредити. Без числа — 5000.", "Ресурси"),
    Cheat("minerals 5000", "Мінерали", "Додає мінерали. Без числа — 5000.", "Ресурси"),
    Cheat("food 5000", "Їжа", "Додає їжу. Без числа — 5000.", "Ресурси"),
    Cheat("alloys 5000", "Сплави", "Додає сплави. Без числа — 5000.", "Ресурси"),
    Cheat("consumer_goods 5000", "Товари", "Додає споживчі товари.", "Ресурси"),
    Cheat("influence 5000", "Вплив", "Додає вплив. Без числа — 5000.", "Ресурси"),
    Cheat("unity 5000", "Єдність", "Додає єдність. Без числа зазвичай 500.", "Ресурси"),
    Cheat("physics 5000", "Очки фізики", "Додає очки дослідження фізики.", "Ресурси"),
    Cheat("society 5000", "Очки суспільства", "Додає очки дослідження суспільства.", "Ресурси"),
    Cheat("engineering 5000", "Очки інженерії", "Додає очки дослідження інженерії.", "Ресурси"),
    Cheat("minor_artifacts 100", "Артефакти", "Додає малі артефакти.", "Ресурси"),
    Cheat("astral_threads 100", "Астральні нитки", "Додає astral threads (DLC Astral Planes).", "Ресурси"),
    Cheat("resource rare_crystals 1000", "Рідкісні кристали", "Додає вказаний ресурс. Формат: resource [тип] [кількість].", "Ресурси"),
    Cheat("resource exotic_gases 1000", "Екзотичні гази", "Додає exotic gases.", "Ресурси"),
    Cheat("resource volatile_motes 1000", "Нестабільні частинки", "Додає volatile motes.", "Ресурси"),
    Cheat("resource sr_living_metal 200", "Живий метал", "Додає living metal.", "Ресурси"),
    Cheat("resource sr_zro 200", "Зро", "Додає zro.", "Ресурси"),
    Cheat("resource sr_dark_matter 200", "Темна матерія", "Додає dark matter.", "Ресурси"),
    Cheat("resource nanites 200", "Наніти", "Додає наніти.", "Ресурси"),
    Cheat("max_resources", "Заповнити склади", "Заповнює всі сховища ресурсів до максимуму.", "Ресурси"),
    Cheat(
        "research_all_technologies",
        "НЕ чіпати: усе дерево",
        "Досліджує ВСЕ звичайне дерево, включно з tech_psionic_theory / cyber / synth. Відкриває Киберизацію, Псі-вознесіння і Синтетизацію. Не для унікальних techs.",
        "НЕБЕЗПЕЧНО",
    ),
    Cheat(
        "research_all_technologies 1 5",
        "НЕ чіпати: дерево + криза",
        "Те саме + технології істот і кризи. Ламає звичайне дерево і шляхи вознесіння.",
        "НЕБЕЗПЕЧНО",
    ),
    Cheat("finish_research", "Закінчити дослідження", "Завершує поточні дослідження і спецпроєкти.", "Наука"),
    Cheat("finish_special_projects", "Спецпроєкти", "Завершує всі спеціальні проєкти.", "Наука"),
    Cheat("techupdate", "Оновити варіанти наук", "Перекидає доступні на вибір технології.", "Наука"),
    Cheat(
        "instant_build",
        "Миттєве будівництво",
        "Перемикач: будівлі, кораблі й апгрейди закінчуються одразу, склади без ліміту. Діє і на ШІ — став паузу.",
        "Будівництво",
    ),
    Cheat("finish_terraform", "Закінчити тераформування", "Завершує всі процеси тераформування.", "Будівництво"),
    Cheat(
        "own",
        "Забрати вибране",
        "Бере під контроль вибраний флот, зоряну базу або планету. Можна передати ID планети.",
        "Планети",
    ),
    Cheat("planet_size 25", "Розмір планети", "Змінює розмір вибраного світу. Потрібно виділити планету.", "Планети"),
    Cheat(
        "planet_class pc_gaia",
        "Тип планети",
        "Вибери світ, потім клікни тут — відкриються всі типи. Без вибору зміниться вся галактика.",
        "Планети",
        (
            _v("planet_class pc_continental", "Континентальна", "Continental — помірний світ."),
            _v("planet_class pc_ocean", "Океанічна", "Ocean."),
            _v("planet_class pc_tropical", "Тропічна", "Tropical."),
            _v("planet_class pc_alpine", "Альпійська", "Alpine."),
            _v("planet_class pc_arctic", "Арктична", "Arctic."),
            _v("planet_class pc_tundra", "Тундра", "Tundra."),
            _v("planet_class pc_arid", "Аридна", "Arid."),
            _v("planet_class pc_desert", "Пустеля", "Desert."),
            _v("planet_class pc_savannah", "Савана", "Savannah."),
            _v("planet_class pc_gaia", "Гея", "Gaia — ідеальний світ."),
            _v("planet_class pc_nuked", "Гробниця", "Tomb World."),
            _v("planet_class pc_relic", "Реліктова", "Relic World."),
            _v("planet_class pc_city", "Екуменополіс", "Ecumenopolis. Далі райони arcology."),
            _v("planet_class pc_hive", "Вуликовий світ", "Hive World."),
            _v("planet_class pc_machine", "Машинний світ", "Machine World."),
            _v("planet_class pc_nanotech", "Нанітовий", "Nanite World."),
            _v("planet_class pc_habitat", "Хабітат", "Orbital Habitat."),
            _v("planet_class pc_ringworld_habitable", "Кільцевий світ", "Ring World, жилий сегмент."),
            _v("planet_class pc_shattered_ring_habitable", "Розбите кільце", "Shattered Ring World."),
            _v("planet_class pc_cosmogenesis_world", "Синайний токарний", "Synaptic Lathe."),
            _v("planet_class pc_barren", "Безплідна", "Barren."),
            _v("planet_class pc_barren_cold", "Холодна безплідна", "Barren (Cold)."),
            _v("planet_class pc_frozen", "Крижана", "Frozen."),
            _v("planet_class pc_molten", "Розплавлена", "Molten."),
            _v("planet_class pc_toxic", "Токсична", "Toxic."),
            _v("planet_class pc_gas_giant", "Газовий гігант", "Gas Giant."),
            _v("planet_class pc_asteroid", "Астероїд", "Asteroid."),
            _v("planet_class pc_shattered", "Розколота", "Shattered — анімація руйнування."),
            _v("planet_class pc_broken", "Зламана", "Broken."),
            _v("planet_class pc_shielded", "Під щитом", "Shielded."),
            _v("planet_class pc_shrouded", "Затінена", "Shrouded."),
            _v("planet_class pc_ai", "AI-світ", "Contingency AI world."),
        ),
    ),
    Cheat("planet_happiness 100", "Щастя планети", "Додає модифікатор щастя вибраній планеті.", "Планети"),
    Cheat("planet_ascension_tier 10", "Ярус вознесіння", "Ставить ascension tier вибраного світу.", "Планети"),
    Cheat("add_pops 0 10", "Додати попів", "Створює попів виду з індексом [id]. 0 — це часто фейковий вид Default, не твої люди. Краще: effect create_pop_group = { species = owner.species size = 1000 }", "Планети"),
    Cheat(
        "effect { random_playable_country = { limit = { is_ai = no } every_owned_pop_group = { limit = { NOT = { is_same_species = owner.species } } kill_pop_group = { pop_group = this percentage = 1 } } } }",
        "Прибрати чужі види",
        "По всій імперії вбиває всіх попів, які не твій founder (Людина). Прибирає Default / По умолчанию. Людей не чіпає. Рядок у списку рас може лишитись з 0.",
        "Планети",
    ),
    Cheat(
        "effect every_owned_pop_group = { kill_pop_group = { pop_group = this percentage = 1 } }",
        "Видалити всіх попів",
        "Вибери колонізовану планету. Зносить усі pop groups (workforce). Колонія лишається, райони теж. Якщо світ одразу скинеться в uninhabited — це ваніль при 0 попів.",
        "Планети",
    ),
    Cheat(
        "effect random_owned_pop_group = { kill_pop_group = { pop_group = this amount = 100 } }",
        "Прибрати 100 попів",
        "Знімає 100 workforce з випадкової групи на вибраній планеті. У 4.x «один поп» = 100.",
        "Планети",
    ),
    Cheat(
        "effect every_owned_pop_group = { kill_pop_group = { pop_group = this percentage = 0.10 } }",
        "Прибрати 10% попів",
        "Ріже кожну групу на вибраній планеті на 10%.",
        "Планети",
    ),
    Cheat("grow_pops", "Місяць росту", "Прокручує один місячний ріст/збірку/занепад попів на вибраній планеті.", "Планети"),
    Cheat("colonize 1", "Колонізувати", "Починає колонізацію вибраного світу копією попа з вказаним ID.", "Планети"),
    Cheat(
        "effect add_deposit = d_minerals_10",
        "Орбітальний ресурс (добувати)",
        "Вибери зірку, астероїд або планету. Звичайні — mining station, дослідження — research station. На одному тілі їх не мішай. Зручніше меню вгорі віджета.",
        "Планети",
        _harvest_variants(),
    ),
    Cheat(
        "effect add_deposit = d_lush_jungle",
        "Родовище / фіча планети",
        "Вибери планету, клікни — фічі з бонусами до районів. Без фіч аграрні/шахтарські/генераторні райони майже не будуються.",
        "Планети",
        (
            _v("effect clear_deposits", "Очистити фічі", "Прибирає всі deposits з вибраного світу."),
            _v("effect reroll_deposits", "Перекидати фічі", "Новий випадковий набір родовищ."),
            _v("effect clear_blockers", "Прибрати блокери", "Зносить усі blockers на планеті."),
            _v("effect add_deposit = d_hot_springs", "Гарячі джерела", "+1 макс. генераторних районів."),
            _v("effect add_deposit = d_arid_highlands", "Аридні височини", "+1 макс. генераторних районів."),
            _v("effect add_deposit = d_buzzing_plains", "Гудячі рівнини", "+1 макс. генераторних районів (статика)."),
            _v("effect add_deposit = d_rushing_waterfalls", "Водоспади", "+2 макс. генераторних районів."),
            _v("effect add_deposit = d_searing_desert", "Пекуча пустеля", "+2 макс. генераторних районів."),
            _v("effect add_deposit = d_frozen_gas_lake", "Замерзле газове озеро", "+2 макс. генераторних районів."),
            _v("effect add_deposit = d_geothermal_vent", "Геотермальні жерла", "+3 макс. генераторних районів."),
            _v("effect add_deposit = d_underwater_vent", "Підводні жерла", "+3 макс. генераторних районів."),
            _v("effect add_deposit = d_tempestous_mountain", "Штормова гора", "+3 макс. генераторних районів."),
            _v("effect add_deposit = d_veiny_cliffs", "Жильні скелі", "+1 макс. шахтарських районів."),
            _v("effect add_deposit = d_mineral_fields", "Мінеральні поля", "+1 макс. шахтарських районів."),
            _v("effect add_deposit = d_prosperous_mesa", "Багата меса", "+2 макс. шахтарських районів."),
            _v("effect add_deposit = d_ore_rich_caverns", "Багаті рудою печери", "+2 макс. шахтарських районів."),
            _v("effect add_deposit = d_rich_mountain", "Багата гора", "+3 макс. шахтарських районів."),
            _v("effect add_deposit = d_submerged_ore_veins", "Підводні жили руди", "+3 макс. шахтарських районів."),
            _v("effect add_deposit = d_ancient_mining_site", "Стародавня шахта", "+5 макс. шахтарських районів."),
            _v("effect add_deposit = d_lichen_fields", "Поля лишайників", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_bountiful_plains", "Родючі рівнини", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_rugged_woods", "Суворі ліси", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_green_hills", "Зелені пагорби", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_forgiving_tundra", "М'яка тундра", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_boggy_fens", "Болотисті низини", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_nutritious_mudland", "Поживні мули", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_natural_farmland", "Природні поля", "+1 макс. аграрних районів."),
            _v("effect add_deposit = d_fungal_caves", "Грибні печери", "+2 макс. аграрних районів."),
            _v("effect add_deposit = d_lush_jungle", "Пишні джунглі", "+2 макс. аграрних районів."),
            _v("effect add_deposit = d_fertile_lands", "Родючі землі", "+2 макс. аграрних районів."),
            _v("effect add_deposit = d_great_river", "Велика ріка", "+2 макс. аграрних районів."),
            _v("effect add_deposit = d_black_soil", "Чорнозем", "+3 макс. аграрних районів."),
            _v("effect add_deposit = d_teeming_reef", "Багатий риф", "+3 макс. аграрних районів."),
            _v("effect add_deposit = d_marvelous_oasis", "Дивовижна оаза", "+3 макс. аграрних районів."),
            _v("effect add_deposit = d_tropical_island", "Тропічний острів", "+3 макс. аграрних районів."),
            _v("effect add_deposit = d_fungal_forest", "Грибний ліс", "+3 макс. аграрних районів."),
            _v("effect add_deposit = d_hyperfertile_valley", "Надродюча долина", "+5 макс. аграрних районів."),
            _v("effect add_deposit = d_harvester_fields", "Поля комбайнів", "+6 макс. аграрних районів."),
            _v("effect add_deposit = d_dust_caverns", "Пилові печери", "+1 слот збору motes."),
            _v("effect add_deposit = d_dust_desert", "Пилова пустеля", "+2 слоти збору motes."),
            _v("effect add_deposit = d_bubbling_swamp", "Булькаюче болото", "+1 слот видобутку газів."),
            _v("effect add_deposit = d_fuming_bog", "Димне болото", "+2 слоти видобутку газів."),
            _v("effect add_deposit = d_crystalline_caverns", "Кристалічні печери", "+1 слот шахт кристалів."),
            _v("effect add_deposit = d_crystal_forest", "Кристалічний ліс", "+2 слоти шахт кристалів."),
            _v("effect add_deposit = d_crystal_reef", "Кристалічний риф", "+2 слоти шахт кристалів."),
            _v("effect add_deposit = d_betharian_deposit", "Поля Бетаріану", "+1 Betharian Power Plant."),
            _v("effect add_deposit = d_alien_pets_deposit", "Ізольована долина", "+1 Alien Zoo."),
            _v("effect add_deposit = d_energy_10", "Орбітальна енергія x10", "Депозит для mining station на нежилому тілі."),
            _v("effect add_deposit = d_minerals_10", "Орбітальні мінерали x10", "Депозит для mining station."),
            _v("effect add_deposit = d_energy_max", "d_energy_max", "Старий/великий енергетичний депозит, якщо ID є в твоїй версії."),
        ),
    ),
    Cheat("effect add_building = building_capital", "Додати будівлю", "Ставить будівлю в основну зону вибраного світу.", "Планети"),
    Cheat("branchoffice", "Філія", "Створює або забирає філію MegaCorp на вибраному світі.", "Планети"),
    Cheat(
        "effect add_district = district_city",
        "Додати район",
        "Вибери колонізовану планету, клікни — відкриються всі райони. Кожен запуск додає один район.",
        "Райони",
        (
            _v(
                "effect while = { count = 5 add_district = district_city }",
                "5 міських одразу",
                "Зміни count і ID району під себе.",
            ),
            _v("effect add_district = district_city", "Міський", "City District — житло."),
            _v("effect add_district = district_industrial", "Індустріальний", "Сплави та товари."),
            _v("effect add_district = district_generator", "Генераторний", "Енергія. Потрібні родовища."),
            _v("effect add_district = district_mining", "Шахтарський", "Мінерали. Потрібні родовища."),
            _v("effect add_district = district_farming", "Аграрний", "Їжа. Потрібні родовища."),
            _v("effect add_district = district_hive", "Вуликовий", "Для hive-імперій."),
            _v("effect add_district = district_nexus", "Нексус", "Для машинних імперій."),
            _v("effect add_district = district_srw_commercial", "Торговий", "Trade District."),
            _v("effect add_district = district_machine_coordination", "Координаційний", "Машинні імперії."),
            _v("effect add_district = district_resort", "Курортний", "Resort world."),
            _v("effect add_district = district_prison", "Тюремний", "Penal Colony."),
            _v("effect add_district = district_prison_industrial", "Тюрма-індустрія", "Prison Industrial."),
            _v("effect add_district = district_slave", "Рабський", "Slave Domicile."),
            _v("effect add_district = district_battle_thrall", "Бойові раби", "Battle Thrall."),
            _v("effect add_district = district_hab_housing", "Хабітат: житло", "Habitation District."),
            _v("effect add_district = district_hab_industrial", "Хабітат: індустрія", "На орбітальному хабітаті."),
            _v("effect add_district = district_hab_science", "Хабітат: наука", "Zero-G Research."),
            _v("effect add_district = district_hab_energy", "Хабітат: реактор", "Reactor District."),
            _v("effect add_district = district_hab_mining", "Хабітат: шахти", "Astro-Mining Bay."),
            _v("effect add_district = district_arcology_housing", "Аркологія: житло", "На екуменополісі (pc_city)."),
            _v("effect add_district = district_arcology_arms_industry", "Аркологія: ливарні", "Foundry — сплави."),
            _v("effect add_district = district_arcology_civilian_industry", "Аркологія: фабрики", "Товари."),
            _v("effect add_district = district_arcology_leisure", "Аркологія: дозвілля", "Leisure Arcology."),
            _v("effect add_district = district_arcology_organic_housing", "Аркологія: святилище", "Для органіків."),
            _v("effect add_district = district_arcology_administrative", "Аркологія: адмін", "Administrative."),
            _v("effect add_district = district_arcology_religious", "Аркологія: храм", "Ecclesiastical."),
            _v("effect add_district = district_rw_city", "Кільце: місто", "City Segment."),
            _v("effect add_district = district_rw_hive", "Кільце: вулик", "Hive Segment."),
            _v("effect add_district = district_rw_nexus", "Кільце: нексус", "Nexus Segment."),
            _v("effect add_district = district_rw_industrial", "Кільце: індустрія", "Industrial Segment."),
            _v("effect add_district = district_rw_generator", "Кільце: генератори", "Generator Segment."),
            _v("effect add_district = district_rw_commercial", "Кільце: торгівля", "Commercial Segment."),
            _v("effect add_district = district_rw_science", "Кільце: наука", "Research Segment."),
            _v("effect add_district = district_rw_farming", "Кільце: ферми", "Agricultural Segment."),
        ),
    ),
    Cheat(
        "create_megastructure dyson_sphere_ruined",
        "Поламана мегаструктура",
        "Відкрий систему, клікни — усі поламані ID. Ремонт зазвичай потребує Mega-Engineering.",
        "Мегаструктури",
        (
            _v("create_megastructure dyson_sphere_ruined", "Сфера Дайсона", "Потрібна зоря в системі."),
            _v("create_megastructure think_tank_ruined", "Science Nexus", "ID: think_tank_ruined."),
            _v("create_megastructure spy_orb_ruined", "Sentry Array", "ID: spy_orb_ruined."),
            _v("create_megastructure matter_decompressor_ruined", "Matter Decompressor", "Потрібна чорна діра."),
            _v("create_megastructure mega_shipyard_ruined", "Mega Shipyard", "Поламаний верф."),
            _v("create_megastructure mega_art_installation_ruined", "Mega Art", "Поламана арт-інсталяція."),
            _v("create_megastructure strategic_coordination_center_ruined", "SCC", "Strategic Coordination Center."),
            _v("create_megastructure interstellar_assembly_ruined", "Interstellar Assembly", "Поламана асамблея."),
            _v("create_megastructure ring_world_ruined", "Сегмент кільця", "Можна ставити кілька сегментів."),
            _v("create_megastructure quantum_catapult_ruined", "Quantum Catapult", "Краще система з пульсаром."),
            _v("create_megastructure gateway_ruined", "Gateway", "Поламану браму можна відремонтувати."),
            _v("create_megastructure hyper_relay_ruined", "Hyper Relay", "Поламаний гіперреле."),
            _v("create_megastructure habitat_central_complex_ruined", "Хабітат", "Ruined Habitat Central Complex."),
            _v("create_megastructure orbital_arc_furnace_destroyed", "Arc Furnace", "ID: orbital_arc_furnace_destroyed."),
            _v("create_megastructure orbital_ring_ruined", "Orbital Ring", "Через консоль часто спавниться криво."),
            _v("create_megastructure dyson_gun_ruined", "Stellar Cannon", "Поламаний зоряний канон."),
            _v("create_megastructure cosmogenesis_world_ruined", "Synaptic Lathe", "Поламаний токарний."),
            _v("create_megastructure gateway_final", "Готовий Gateway", "Робоча брама, не поламана."),
        ),
    ),
    Cheat("survey", "Дослідити все", "Досліджує всі небесні тіла. Потрібен хоча б один науковий корабель.", "Карта"),
    Cheat("intel", "Відкрити галактику", "Дає огляд усієї галактики (туман війни).", "Карта"),
    Cheat("communications", "Зв'язок з усіма", "Встановлює комунікацію з усіма імперіями, анклавами і Shroud.", "Карта"),
    Cheat("contact", "Перший контакт", "Починає first contact з усіма імперіями.", "Карта"),
    Cheat("activate_gateways", "Увімкнути брами", "Активує всі gateway у галактиці.", "Карта"),
    Cheat("invincible", "Невразливість", "Твої кораблі не отримують шкоди. Повтор вимикає.", "Флот"),
    Cheat("create_navy 0.5", "Створити флот", "Будує флот з твоїх останніх дизайнів на вказану частку naval cap. 1 = 100%.", "Флот"),
    Cheat("add_ship Corvette", "Додати корабель", "Створює флот з одного корабля дизайну. Tab показує імена NPC.", "Флот"),
    Cheat(
        "add_ship Science",
        "Науковий корабель",
        "Спавнить science ship біля столиці. Якщо не з’явився — після add_ship натисни Tab і вибери свій дизайн.",
        "Флот",
    ),
    Cheat(
        "add_ship Constructor",
        "Будівельний корабель",
        "Спавнить construction ship біля столиці. Tab показує точну назву дизайну.",
        "Флот",
    ),
    Cheat(
        "effect { random_playable_country = { limit = { is_ai = no } create_fleet = { effect = { set_owner = this create_ship = { name = random random_existing_design = science } } } } }",
        "Науковий (гарантовано)",
        "Бере твій існуючий дизайн science і ставить новий флот. Працює, навіть якщо назва дизайну не Science.",
        "Флот",
    ),
    Cheat(
        "effect { random_playable_country = { limit = { is_ai = no } create_fleet = { effect = { set_owner = this create_ship = { name = random random_existing_design = constructor } } } } }",
        "Будівельний (гарантовано)",
        "Бере твій існуючий дизайн constructor і ставить новий флот.",
        "Флот",
    ),
    Cheat("damage 500", "Пошкодити флот", "Усі кораблі вибраного флоту отримують вказану шкоду корпусу.", "Флот"),
    Cheat("ai", "Вимкнути ШІ", "Перемикає штучний інтелект імперій. Повтор вмикає знову.", "Флот"),
    Cheat("skills 10", "Рівень лідерів", "Додає рівні навичок усім найнятим лідерам. Без числа — 1.", "Лідери"),
    Cheat("add_trait_leader 0 leader_trait_eager", "Риса лідеру", "Додає рису лідеру за ID. Спочатку debugtooltip.", "Лідери"),
    Cheat("hire_all_leaders", "Найняти пул", "Наймати всіх лідерів з поточного пулу.", "Лідери"),
    Cheat("update_leader_pool", "Оновити пул лідерів", "Оновлює список доступних лідерів.", "Лідери"),
    Cheat("election", "Вибори", "Запускає вибори правителя.", "Лідери"),
    Cheat(
        "activate_all_traditions",
        "НЕ чіпати: усі традиції",
        "Приймає Cybernetics + Psionics + Synthetics ОДРАЗУ. Саме це стартує три ситуації вознесіння разом.",
        "НЕБЕЗПЕЧНО",
    ),
    Cheat(
        "activate_ascension_perk ap_technological_ascendancy",
        "Перк вознесіння",
        "Активує ОДИН perk. Не став ap_mind_over_matter / ap_the_flesh_is_weak / ap_synthetic_evolution, якщо не хочеш шлях вознесіння.",
        "Держава",
    ),
    Cheat("unlock_edicts", "Усі едикти", "Відкриває всі едикти.", "Держава"),
    Cheat("free_government", "Вільний уряд", "Можна міняти уряд без таймера і обмежень civic.", "Держава"),
    Cheat("free_policies", "Вільні політики", "Можна міняти політики та права видів без обмежень.", "Держава"),
    Cheat("add_relic all", "Усі реліквії", "Видає всі реліквії. Можна вказати конкретний ID замість all.", "Держава"),
    Cheat("advance_council_agenda 1000", "Прогрес ради", "Додає прогрес порядку денного ради. Без числа — одразу готово.", "Держава"),
    Cheat("debug_yesmen", "ШІ завжди згоден", "ШІ завжди приймає твої пропозиції. Повтор вимикає.", "Дипломатія"),
    Cheat("add_opinion 1 0 100", "Думка", "Імперія [source] краще ставиться до [target] на [кількість].", "Дипломатія"),
    Cheat("add_trust 1 0 100", "Довіра", "Збільшує trust між імперіями.", "Дипломатія"),
    Cheat("add_intel 1 100", "Розвіддані", "Додає intel щодо цілі.", "Дипломатія"),
    Cheat("force_integrate 2", "Інтегрувати імперію", "Миттєво інтегрує цільову імперію в твою.", "Дипломатія"),
    Cheat("annex 3", "Анексувати", "Забирає всі світи й бази цільової імперії.", "Дипломатія"),
    Cheat("play 0", "Грати за імперію", "Перемикає керування на імперію з цим ID. 0 — зазвичай ти.", "Дипломатія"),
    Cheat("observe", "Режим спостерігача", "Виходить у observer. Повернення: play 0. Не знімай паузу — ШІ перехопить твою імперію.", "Дипломатія"),
    Cheat("federation_add_experience 1000", "Досвід федерації", "Додає досвід твоїй федерації.", "Дипломатія"),
    Cheat("federation_add_cohesion 200", "Згуртованість федерації", "Додає cohesion федерації.", "Дипломатія"),
    Cheat("add_anomaly life_asteroid_category", "Аномалія", "Додає аномалію на вибране тіло. Tab показує ID.", "Події"),
    Cheat("event crisis.199", "Криза Prethoryn", "Запускає кризу Prethoryn Scourge.", "Події"),
    Cheat("event crisis.1000", "Криза Unbidden", "Запускає кризу Unbidden.", "Події"),
    Cheat("event crisis.2000", "Криза Contingency", "Запускає кризу Contingency.", "Події"),
    Cheat("event galcom.16", "Галактична спільнота", "Подія про створення Galactic Community.", "Події"),
    Cheat("finish_arc_stage", "Розкопки", "Завершує поточний розділ археології. Вибери світ і науковий корабель.", "Події"),
)


def grouped_cheats() -> list[tuple[str, list[Cheat]]]:
    groups: dict[str, list[Cheat]] = {}
    order: list[str] = []
    for cheat in CHEATS:
        if cheat.category not in groups:
            groups[cheat.category] = []
            order.append(cheat.category)
        groups[cheat.category].append(cheat)
    return [(name, groups[name]) for name in order]


def _cheat_matches(cheat: Cheat, needle: str) -> bool:
    return (
        needle in cheat.command.casefold()
        or needle in cheat.title.casefold()
        or needle in cheat.description.casefold()
        or needle in cheat.category.casefold()
    )


def filter_cheats(query: str, source: tuple[Cheat, ...] | None = None) -> list[Cheat]:
    pool = CHEATS if source is None else source
    needle = query.strip().casefold()
    if not needle:
        return list(pool)
    result: list[Cheat] = []
    for cheat in pool:
        own_match = _cheat_matches(cheat, needle)
        matched_variants = tuple(variant for variant in cheat.variants if _cheat_matches(variant, needle))
        if matched_variants:
            result.append(replace(cheat, variants=matched_variants))
        elif own_match:
            result.append(cheat)
    return result
