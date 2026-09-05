"""Catalog and installer for Stellaris 4.x `run filename.txt` scripts."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from stellaris_saves import SAVE_RELATIVE


SCRIPTS_DIR = Path(__file__).resolve().parent / "run_scripts"


@dataclass(frozen=True)
class RunScript:
    filename: str
    title: str
    group: str
    select: str
    creates: str


def stellaris_documents_dir() -> Path:
    return Path.home() / SAVE_RELATIVE.parent


RUN_SCRIPTS: tuple[RunScript, ...] = (
    RunScript(
        "supersystem.txt",
        "Суперсистема",
        "Суперсистема",
        "Центральна зірка (НЕ столиця). Скрипт ЗНЕСЕ систему й поставить усе заново",
        "Зносить планети/станції/мега/базу. 20 еку + 20 гая 78 без власника, 20 астероїдів, хабітати 78, майданчики megasystem_all_compatible",
    ),
    RunScript(
        "eventsystem.txt",
        "Івент-система поряд",
        "Суперсистема",
        "Зірка суперсистеми (або будь-яка зірка). Поставить НОВУ систему поруч по гіперлінії",
        "16 незаселених світів 78 під colony events, археологія не пройдена, rift не завершений, ruined меги. Цитадель id 0",
    ),
    RunScript(
        "megasystem_all_compatible.txt",
        "Усі сумісні мегасооруження",
        "Мегасистеми",
        "Центральна зірка в системі, якою ти володієш",
        "Майданчики Nexus, Sentry, SCC, Mega Art, Assembly, Shipyard, Gateway (_0). Далі добудовуєш у грі",
    ),
    RunScript(
        "system_dyson.txt",
        "Сфера Дайсона",
        "Мегасистеми",
        "Звичайна зірка (G/K/F/A/B/M), не чорна діра",
        "sc_g + майданчик Dyson Sphere (dyson_sphere_0). Внутрішні планети гра може зжерти",
    ),
    RunScript(
        "system_dyson_swarm.txt",
        "Dyson Swarm",
        "Мегасистеми",
        "Звичайна зірка",
        "Перша стадія Dyson Swarm (dyson_swarm_1). Не сумісний зі сферою Дайсона",
    ),
    RunScript(
        "system_ringworld.txt",
        "Ring World",
        "Мегасистеми",
        "Звичайна зірка",
        "Майданчик ring_world_1 (не 4 готові секції). Внутрішні планети/астероїди можуть зникнути",
    ),
    RunScript(
        "system_matter_decompressor.txt",
        "Matter Decompressor",
        "Мегасистеми",
        "Зірка / чорна діра",
        "Ставить sc_black_hole і майданчик Matter Decompressor (_0)",
    ),
    RunScript(
        "system_quantum_catapult.txt",
        "Quantum Catapult",
        "Мегасистеми",
        "Зірка (краще пульсар)",
        "Ставить sc_pulsar і майданчик Quantum Catapult (_0)",
    ),
    RunScript(
        "system_stellar_cannon.txt",
        "Stellar Cannon",
        "Мегасистеми",
        "Звичайна зірка",
        "Майданчик Stellar Cannon (dyson_gun_0). Конфліктує з Dyson Sphere / Swarm / Catapult",
    ),
    RunScript(
        "system_arc_furnace.txt",
        "Arc Furnace",
        "Мегасистеми",
        "Розплавлена планета (pc_molten)",
        "Перша стадія Arc Furnace (_1) на вибраній molten-планеті",
    ),
    RunScript(
        "ecu78_capital_planet.txt",
        "Столиця 78 — планета",
        "Екуменополіс 78",
        "Колонізована планета",
        "pc_city, розмір 78. По 70 housing/urban_1/2/3 (ignore_cap). Без попів",
    ),
    RunScript(
        "ecu78_capital_ring.txt",
        "Столиця 78 — кільце",
        "Екуменополіс 78",
        "1) планета для спавну  2) саме Orbital Ring для модулів",
        "Спавнить restored ring і намагається заповнити універсальні модулі",
    ),
    RunScript(
        "ecu78_alloys_planet.txt",
        "Сплави 78 — планета",
        "Екуменополіс 78",
        "Колонізована планета",
        "Foundry arcology, foundry_3, попи під робочі місця",
    ),
    RunScript(
        "ecu78_alloys_ring.txt",
        "Сплави 78 — кільце",
        "Екуменополіс 78",
        "Планета, потім Orbital Ring",
        "Ring + alloy/mineral hubs, shipyard, anchorage",
    ),
    RunScript(
        "ecu78_consumer_goods_planet.txt",
        "Товари 78 — планета",
        "Екуменополіс 78",
        "Колонізована планета",
        "Factory arcology, factory_3, попи",
    ),
    RunScript(
        "ecu78_consumer_goods_ring.txt",
        "Товари 78 — кільце",
        "Екуменополіс 78",
        "Планета, потім Orbital Ring",
        "Ring + consumer/trade hubs",
    ),
    RunScript(
        "ecu78_unity_planet.txt",
        "Unity 78 — планета",
        "Екуменополіс 78",
        "Колонізована планета",
        "Administrative arcology, bureaucratic_3",
    ),
    RunScript(
        "ecu78_unity_ring.txt",
        "Unity 78 — кільце",
        "Екуменополіс 78",
        "Планета, потім Orbital Ring",
        "Ring + bureaucracy hub, habitation",
    ),
    RunScript(
        "ecu78_research_planet.txt",
        "Наука 78 — планета",
        "Екуменополіс 78",
        "Колонізована планета",
        "Research arcology, lab_3, institute",
    ),
    RunScript(
        "ecu78_research_ring.txt",
        "Наука 78 — кільце",
        "Екуменополіс 78",
        "Планета, потім Orbital Ring",
        "Ring: habitation/щит (окремого research-hub немає)",
    ),
    RunScript(
        "ecu78_trade_planet.txt",
        "Торгівля 78 — планета",
        "Екуменополіс 78",
        "Колонізована планета",
        "Trade arcology, stock exchange",
    ),
    RunScript(
        "ecu78_trade_ring.txt",
        "Торгівля 78 — кільце",
        "Екуменополіс 78",
        "Планета, потім Orbital Ring",
        "Ring + trade hub і galactic stock exchange",
    ),
    RunScript(
        "ecu78_fortress_planet.txt",
        "Фортеця 78 — планета",
        "Екуменополіс 78",
        "Колонізована планета",
        "Fortress arcology, fortress, academy, щит",
    ),
    RunScript(
        "ecu78_fortress_ring.txt",
        "Фортеця 78 — кільце",
        "Екуменополіс 78",
        "Планета, потім Orbital Ring",
        "Ring: гармати, ангари, anchorage, shield generator",
    ),
    RunScript(
        "gaia78_capital_planet.txt",
        "Гея 78 — планета",
        "Гея 78",
        "Колонізована планета",
        "pc_gaia 78. По 3 кожної фічі generator/mining/farming з меню. Без спецдепозитів і без примусових 70 районів. Без попів",
    ),
    RunScript(
        "ring_research.txt",
        "Секція: наука",
        "Кільцевий світ",
        "Колонізована секція Ring World",
        "Забудова science segments + лабораторії + попи",
    ),
    RunScript(
        "ring_trade.txt",
        "Секція: торгівля",
        "Кільцевий світ",
        "Колонізована секція Ring World",
        "Commercial segments + біржі",
    ),
    RunScript(
        "ring_food.txt",
        "Секція: їжа",
        "Кільцевий світ",
        "Колонізована секція Ring World",
        "Farming segments + hydroponics",
    ),
    RunScript(
        "ring_unity.txt",
        "Секція: unity",
        "Кільцевий світ",
        "Колонізована секція Ring World",
        "City segments + administrative buildings",
    ),
    RunScript(
        "ring_general.txt",
        "Секція: змішана",
        "Кільцевий світ",
        "Колонізована секція Ring World",
        "Місто / індустрія / наука / ферми",
    ),
    RunScript(
        "ring_alloys.txt",
        "Секція: сплави",
        "Кільцевий світ",
        "Колонізована секція Ring World",
        "Industrial + foundry zone",
    ),
    RunScript(
        "ring_energy.txt",
        "Секція: енергія",
        "Кільцевий світ",
        "Колонізована секція Ring World",
        "Generator segments",
    ),
    RunScript(
        "orbital_resources_300.txt",
        "Mining 300",
        "Орбітальні депозити",
        "Нежива планета / астероїд / зірка",
        "Energy, minerals, alloys, food, consumer goods по 300. Далі mining station",
    ),
    RunScript(
        "orbital_resources_3000.txt",
        "Mining 3000",
        "Орбітальні депозити",
        "Нежива планета / астероїд / зірка",
        "Energy, minerals, alloys, food, consumer goods по 3000. Далі mining station",
    ),
    RunScript(
        "orbital_energy_10000.txt",
        "Енергія 10000",
        "Орбітальні депозити",
        "Нежива планета / астероїд / зірка",
        "Energy ×10000 (10×100 d_energy_10). Далі mining station",
    ),
    RunScript(
        "orbital_energy_100000.txt",
        "Енергія 100000",
        "Орбітальні депозити",
        "Нежива планета / астероїд / зірка",
        "Energy ×100000 (10×10000). Далі mining station",
    ),
    RunScript(
        "orbital_science_500.txt",
        "Science 500×3",
        "Орбітальні депозити",
        "Нежива планета / астероїд / зірка без mining-депозитів",
        "Physics/Society/Engineering по 500. Далі research station",
    ),
    RunScript(
        "orbital_science_5000.txt",
        "Science 5000×3",
        "Орбітальні депозити",
        "Нежива планета / астероїд / зірка без mining-депозитів",
        "Physics/Society/Engineering по 5000. Далі research station",
    ),
    RunScript(
        "orbital_special_resources_100.txt",
        "Спец. 100 — читай README",
        "Орбітальні депозити",
        "Не запускати: mining і research треба на різних тілах",
        "Вказівник на orbital_special_mining_100 і orbital_special_research_100",
    ),
    RunScript(
        "orbital_special_mining_100.txt",
        "Спец. mining 100",
        "Орбітальні депозити",
        "Нежива планета без research-депозитів",
        "Гази, кристали, motes, living metal, артефакти, trade",
    ),
    RunScript(
        "orbital_special_mining_1000.txt",
        "Спец. mining 1000",
        "Орбітальні депозити",
        "Нежива планета без research-депозитів",
        "Гази, кристали, motes, living metal, артефакти, trade ×1000",
    ),
    RunScript(
        "orbital_special_research_100.txt",
        "Спец. research 100",
        "Орбітальні депозити",
        "Нежива планета без mining-депозитів",
        "Dark matter, zro, nanites, astral, artifacts research ×100, unity ×300",
    ),
    RunScript(
        "orbital_special_research_1000.txt",
        "Спец. research 1000",
        "Орбітальні депозити",
        "Нежива планета без mining-депозитів",
        "Dark matter, zro, nanites, astral, artifacts research ×1000, unity ×3000",
    ),
    RunScript(
        "habitat_system_setup.txt",
        "Підготовка системи",
        "Хабітат",
        "Зірка системи, якою ти володієш",
        "Депозити energy/minerals на нежилих тілах для district cap",
    ),
    RunScript(
        "habitat_spawn_central.txt",
        "Спавн Central Complex",
        "Хабітат",
        "Нежила планета в підготовленій системі",
        "habitat_central_complex на вибраному тілі",
    ),
    RunScript(
        "habitat_spawn_major.txt",
        "Спавн Major Orbital",
        "Хабітат",
        "Інша нежила планета з депозитом",
        "habitat_major_orbital",
    ),
    RunScript(
        "habitat_spawn_minor.txt",
        "Спавн Minor Orbital",
        "Хабітат",
        "Астероїд або дрібне тіло з депозитом",
        "habitat_minor_orbital",
    ),
    RunScript(
        "habitat_research.txt",
        "Хабітат: наука",
        "Хабітат",
        "Колонізований Habitat Central Complex",
        "Science districts, labs, попи",
    ),
    RunScript(
        "habitat_trade.txt",
        "Хабітат: торгівля",
        "Хабітат",
        "Колонізований хабітат",
        "Commercial districts",
    ),
    RunScript(
        "habitat_industry.txt",
        "Хабітат: індустрія",
        "Хабітат",
        "Колонізований хабітат",
        "Industrial districts, foundry/factory",
    ),
    RunScript(
        "habitat_fortress.txt",
        "Хабітат: фортеця",
        "Хабітат",
        "Колонізований хабітат",
        "Житло + fortress/stronghold (окремого fortress-district немає)",
    ),
    RunScript(
        "habitat_mining.txt",
        "Хабітат: шахти",
        "Хабітат",
        "Колонізований хабітат",
        "Mining districts. Краще після system_setup",
    ),
    RunScript(
        "habitat_energy.txt",
        "Хабітат: енергія",
        "Хабітат",
        "Колонізований хабітат",
        "Reactor districts",
    ),
    RunScript(
        "tech_insights.txt",
        "Insight Technologies — НЕ до Insightful",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "13 Pre-FTL insight techs. Achievement Insightful = num_insight_techs >= 12. Не запускати до achievement, якщо хочеш Insightful з спостереження",
    ),
    RunScript(
        "tech_insights_AFTER_achievement.txt",
        "Insight Technologies — ПІСЛЯ Insightful",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Ті самі 13 insight techs. Запускати лише після Insightful",
    ),
    RunScript(
        "tech_precursors.txt",
        "Precursor Secrets (усі ланцюги)",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "tech_secrets_* усіх ванільних precursor. Без relics і без flags завершення. Inetian/AdAkkaria не мають secret-tech",
    ),
    RunScript(
        "tech_archaeotech.txt",
        "Archaeotechnologies",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Усі archaeo зброя/броня/щити/будівлі. Компоненти потребують Minor Artifacts на будівництво, не AP",
    ),
    RunScript(
        "tech_guardians.txt",
        "Guardian / Leviathan techs",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Dragonscales, Enigmatic Encoder/Decoder, Scavenger nanites. НЕ вбиває Guardian і не ставить killed flags",
    ),
    RunScript(
        "tech_fallen_empire.txt",
        "Fallen Empire / Dark Matter",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "DM core/thrusters/deflectors + FE будівлі. Звичайні prereqs (shields_5 тощо) не видаються. FE отримають штраф думки",
    ),
    RunScript(
        "tech_crisis.txt",
        "Crisis reverse-engineering",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Unbidden/Horror matter disintegrator, Prethoryn missiles/craft, Cetana techs. Кризу НЕ запускає",
    ),
    RunScript(
        "tech_lcluster.txt",
        "L-Cluster nanites (безпечні)",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Nanite transmutation + neuroregeneration. НЕ відкриває L-Gates і не вибирає outcome",
    ),
    RunScript(
        "tech_lcluster_DANGEROUS.txt",
        "L-Cluster DANGEROUS",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "tech_lgate_activation + repeatable clue. Ламає/прискорює L-Gate chain. Не в master",
    ),
    RunScript(
        "tech_psionic_event.txt",
        "Psionic / Shroud event techs",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Бар'єри, щити, shroud-зброя, psi jump. Без ethics, AP, covenant, End of the Cycle",
    ),
    RunScript(
        "tech_rare_resources.txt",
        "Рідкісні стратегічні ресурси",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Living Metal / Zro / Dark Matter mining + Astral Harvesting. Звичайні motes/gases/crystals не видаються",
    ),
    RunScript(
        "tech_events_unique.txt",
        "Інші unique event techs",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Curator labs, Caravan trash, Skrand, Null Void, Extreme Frontiers, identity policies",
    ),
    RunScript(
        "tech_space_fauna.txt",
        "Space fauna techs",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Amoeba/Tiyanki/crystal/drones/clouds/cutholoid/voidworm. Фауну не знищує",
    ),
    RunScript(
        "tech_astral.txt",
        "Astral Planes — Rift Sphere",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "tech_rift_sphere (unlock exploration). Ріфти не завершує і outcome не ставить",
    ),
    RunScript(
        "tech_all_specific.txt",
        "Усі специфічні технології",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "Insights + precursor/archaeotech/guardians/fauna/FE/crisis/L-Cluster/astral/event. Без вознесіння, Cosmogenesis, covenant, L-Gate open",
    ),
    RunScript(
        "tech_all_unique.txt",
        "Усі безпечні unique techs",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "128 безпечних ID. Без insights (Insightful), без L-Gate open, без worm/covenant/cosmogenesis",
    ),
    RunScript(
        "tech_all_unique_DANGEROUS.txt",
        "Unique DANGEROUS (ланцюги/path)",
        "Унікальні технології",
        "Нічого (команда на гравця)",
        "L-Gate open, Horizon Signal worm, covenants, psionic aura flags, Cosmogenesis path",
    ),
    RunScript(
        "pop_traits_353.txt",
        "Топ-5 трейтів (ID 353)",
        "Попи",
        "Будь-де (застосовується до pop group 353)",
        "Psionic, Erudite, Robust, Fertile, Cybernetic для поп-групи 353",
    ),
)


def run_command(filename: str) -> str:
    return f"run {filename}"


DOC_ONLY_SCRIPTS = frozenset(
    {
        "README.txt",
        "ACHIEVEMENT_WARNINGS.txt",
        "UNIQUE_TECH_REPORT.txt",
        "TECH_INSIGHTS_README.txt",
    }
)


def install_run_scripts() -> tuple[Path, int]:
    source = SCRIPTS_DIR
    if not source.is_dir():
        raise FileNotFoundError(f"Немає папки зі скриптами: {source}")
    dest = stellaris_documents_dir()
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    catalog = {script.filename for script in RUN_SCRIPTS}
    for path in sorted(source.glob("*.txt")):
        if path.name in DOC_ONLY_SCRIPTS:
            shutil.copy2(path, dest / path.name)
            continue
        if path.name not in catalog:
            continue
        shutil.copy2(path, dest / path.name)
        count += 1
    return dest, count
