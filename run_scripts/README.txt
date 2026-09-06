Stellaris 4.x run-скрипти (серпень 2026)
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
pop_traits_353.txt | Psionic/Erudite/Robust/Fertile/Cybernetic | нічого (pop group 353)
pop_357_*.txt | один унікальний івентовий перк на файл | нічого (раса або pop group 357)

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

Унікальні івентові перки (раса 357)
-----------------------------------
Кожен файл додає ОДИН перк. Запускай лише потрібні.
Команда: add_trait_species 357 <trait>  (лише вид 357, не поп-групи).
Перегенерувати: python3 write_pop_357.py

pop_357_brainslug.txt | Brain Slug Host
pop_357_bioadaptability.txt | Speed Demon зелений
pop_357_limited_regeneration.txt | Speed Demon синій
pop_357_social_pheromones.txt | Speed Demon червоний
pop_357_nivlac.txt | Nivlac
pop_357_enigmatic_intelligence.txt | Uplifted (Enigmatic Cache)
pop_357_plasmic.txt | Plasmic
pop_357_psionic_ephapse.txt | Psionic Ephapse
pop_357_slimeborn.txt | Slimespawn
pop_357_numistic.txt | Numistic Administration
pop_357_bloomed.txt | Bloomed (Gaia Seeders)

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
