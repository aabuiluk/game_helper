#!/usr/bin/env python3
"""Find Stellaris saves and toggle Ironman on or off."""

from __future__ import annotations

import functools
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SAVE_RELATIVE = Path("Documents") / "Paradox Interactive" / "Stellaris" / "save games"
LINUX_SAVE_RELATIVE = Path(".local/share/Paradox Interactive/Stellaris/save games")
STEAM_APP_ID = "281990"
FALLBACK_ACHIEVEMENT_MAX_ID = 219

IRONMAN_GAMESTATE = re.compile(rb"(?m)^(\t*)ironman=(yes|no)[ \t]*\r?$")
IRONMAN_META = re.compile(rb"(?m)^ironman=(yes|no)[ \t]*\r?\n?")
CHEATED_ON_SAVE = re.compile(rb"(?m)^cheated_on_save=(yes|no)[ \t]*\r?$")
RANDOM_LOG_DAY = re.compile(rb"(?m)^random_log_day=\d+[ \t]*\r?\n")
ROOT_ACHIEVEMENT_BLOCK = re.compile(rb"(?m)^achievement=\s*\{[^{}]*\}")
ROOT_CLUSTERS = re.compile(rb"(?m)^clusters=")
META_NAME = re.compile(rb'(?m)^name="([^"]*)"')
META_DATE = re.compile(rb'(?m)^date="([^"]*)"')
ACHIEVEMENT_ID = re.compile(rb"\bid\s*=\s*(\d+)")


@dataclass
class SaveInfo:
    path: Path
    empire: str
    date: str
    ironman: bool
    modified: datetime
    cheated: bool = False

    @property
    def campaign(self) -> str:
        return self.path.parent.name


@dataclass
class SaveScanResult:
    saves: list[SaveInfo]
    skipped: list[tuple[Path, str]]
    roots: list[Path]


def save_roots() -> list[Path]:
    home = Path.home()
    roots: list[Path] = []
    for candidate in (
        home / SAVE_RELATIVE,
        home / LINUX_SAVE_RELATIVE,
        Path("/mnt/c") / "Users" / home.name / SAVE_RELATIVE,
    ):
        if candidate.is_dir():
            roots.append(candidate)

    steam_userdata = (
        home / "Library/Application Support/Steam/userdata",
        home / ".steam/steam/userdata",
        home / ".local/share/Steam/userdata",
        Path("C:/Program Files (x86)/Steam/userdata"),
    )
    for userdata in steam_userdata:
        if not userdata.is_dir():
            continue
        for remote in userdata.glob(f"*/{STEAM_APP_ID}/remote/save games"):
            if remote.is_dir():
                roots.append(remote)

    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(root)
    return unique


def _skip_save_path(path: Path) -> bool:
    if path.name.startswith("."):
        return True
    skip_parts = {"ironman_backups", ".idea"}
    return any(part in skip_parts for part in path.parts)


def _slot_name(path: Path) -> str:
    if path.is_dir():
        return path.name
    name = path.name
    if name.endswith(".sav"):
        return Path(name).stem
    if name.endswith(".zip"):
        base = name[:-4]
        if base.endswith(".sav"):
            return base[:-4]
        return base
    return path.stem


def _save_slot_key(path: Path) -> tuple[Path, str]:
    return path.parent.resolve(), _slot_name(path)


def _save_modified(path: Path) -> float:
    if path.is_dir():
        return max(
            (path / "gamestate").stat().st_mtime,
            (path / "meta").stat().st_mtime,
        )
    return path.stat().st_mtime


def save_display_name(path: Path) -> str:
    campaign = path.parent.name
    slot = f"{path.name}/" if path.is_dir() else path.name
    return f"{campaign}/{slot}"


def _discover_save_paths(root: Path) -> list[Path]:
    found: list[Path] = []
    seen_dirs: set[Path] = set()

    for sav in root.rglob("*.sav"):
        if _skip_save_path(sav):
            continue
        found.append(sav)

    for archive in root.rglob("*.zip"):
        if _skip_save_path(archive):
            continue
        if archive.parent.resolve() == root.resolve():
            continue
        found.append(archive)

    for gamestate in root.rglob("gamestate"):
        if _skip_save_path(gamestate):
            continue
        save_dir = gamestate.parent
        if not (save_dir / "meta").is_file():
            continue
        resolved = save_dir.resolve()
        if resolved in seen_dirs:
            continue
        seen_dirs.add(resolved)
        found.append(save_dir)

    return found


def _read_save_files(path: Path) -> dict[str, bytes]:
    if path.is_dir():
        gamestate = path / "gamestate"
        meta = path / "meta"
        if not gamestate.is_file() or not meta.is_file():
            raise ValueError(f"{path}: немає gamestate/meta")
        return {"gamestate": gamestate.read_bytes(), "meta": meta.read_bytes()}

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = {"gamestate", "meta"} - names
        if missing:
            raise ValueError(f"{path.name}: немає файлів {', '.join(sorted(missing))}")
        return {name: archive.read(name) for name in ("gamestate", "meta")}


def _read_zip_text_files(path: Path) -> dict[str, bytes]:
    return _read_save_files(path)


def _meta_field(meta: bytes, pattern: re.Pattern[bytes], fallback: str = "?") -> str:
    match = pattern.search(meta)
    if not match:
        return fallback
    return match.group(1).decode("utf-8", errors="replace")


def _is_ironman(files: dict[str, bytes]) -> bool:
    meta_match = IRONMAN_META.search(files["meta"])
    if meta_match:
        return meta_match.group(1) == b"yes"
    game_match = IRONMAN_GAMESTATE.search(files["gamestate"])
    return bool(game_match and game_match.group(2) == b"yes")


def _is_cheated(gamestate: bytes) -> bool:
    match = CHEATED_ON_SAVE.search(gamestate)
    return bool(match and match.group(1) == b"yes")


def inspect_save(path: Path) -> SaveInfo:
    files = _read_save_files(path)
    meta = files["meta"]
    gamestate_head = files["gamestate"][:32768]
    meta_match = IRONMAN_META.search(meta)
    return SaveInfo(
        path=path,
        empire=_meta_field(meta, META_NAME, path.parent.name),
        date=_meta_field(meta, META_DATE),
        ironman=bool(meta_match and meta_match.group(1) == b"yes"),
        modified=datetime.fromtimestamp(_save_modified(path)),
        cheated=_is_cheated(gamestate_head),
    )


def scan_saves() -> SaveScanResult:
    saves: list[SaveInfo] = []
    skipped: list[tuple[Path, str]] = []
    roots = save_roots()
    best: dict[tuple[Path, str], tuple[float, Path]] = {}
    for root in roots:
        for path in _discover_save_paths(root):
            key = _save_slot_key(path)
            mtime = _save_modified(path)
            current = best.get(key)
            if current is None or mtime >= current[0]:
                best[key] = (mtime, path)

    for _, path in best.values():
        try:
            saves.append(inspect_save(path))
        except (ValueError, zipfile.BadZipFile, OSError) as error:
            skipped.append((path, str(error)))
    saves.sort(key=lambda item: item.modified, reverse=True)
    return SaveScanResult(saves=saves, skipped=skipped, roots=roots)


def find_saves() -> list[SaveInfo]:
    return scan_saves().saves


def stellaris_running() -> bool:
    try:
        result = subprocess.run(
            ["pgrep", "-if", "stellaris"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0 and bool(result.stdout.strip())


def _set_gamestate_ironman(gamestate: bytes, enabled: bool) -> bytes:
    value = b"yes" if enabled else b"no"
    if not IRONMAN_GAMESTATE.search(gamestate):
        raise ValueError("У gamestate немає рядка ironman=yes/no")
    return IRONMAN_GAMESTATE.sub(rb"\1ironman=" + value, gamestate, count=1)


def _set_meta_ironman(meta: bytes, enabled: bool) -> bytes:
    cleaned = IRONMAN_META.sub(b"", meta).rstrip(b"\r\n")
    if enabled:
        return cleaned + b"\nironman=yes\n"
    return cleaned + b"\n"


def _stellaris_achievements_file() -> Path | None:
    home = Path.home()
    for candidate in (
        home / "Library/Application Support/Steam/steamapps/common/Stellaris/common/achievements.txt",
        home / ".steam/steam/steamapps/common/Stellaris/common/achievements.txt",
        home / ".local/share/Steam/steamapps/common/Stellaris/common/achievements.txt",
        Path("C:/Program Files (x86)/Steam/steamapps/common/Stellaris/common/achievements.txt"),
    ):
        if candidate.is_file():
            return candidate
    return None


@functools.lru_cache(maxsize=1)
def _achievement_ids() -> tuple[int, ...]:
    path = _stellaris_achievements_file()
    if path is not None:
        ids = [int(match.group(1)) for match in ACHIEVEMENT_ID.finditer(path.read_bytes())]
        if ids:
            return tuple(range(1, max(ids) + 1))
    return tuple(range(1, FALLBACK_ACHIEVEMENT_MAX_ID + 1))


def _achievement_block() -> bytes:
    numbers = " ".join(str(item) for item in _achievement_ids())
    return f"achievement=\n{{\n\t{numbers} \n}}\n".encode("ascii")


def _set_cheated_on_save(gamestate: bytes, cheated: bool) -> bytes:
    value = b"yes" if cheated else b"no"
    replacement = b"cheated_on_save=" + value
    if CHEATED_ON_SAVE.search(gamestate):
        return CHEATED_ON_SAVE.sub(replacement, gamestate, count=1)
    line = replacement + b"\n"
    log_day = RANDOM_LOG_DAY.search(gamestate)
    if log_day:
        return gamestate[: log_day.end()] + line + gamestate[log_day.end() :]
    return line + gamestate


def _ensure_achievement_block(gamestate: bytes) -> bytes:
    if ROOT_ACHIEVEMENT_BLOCK.search(gamestate):
        return gamestate
    clusters = ROOT_CLUSTERS.search(gamestate)
    if not clusters:
        raise ValueError("У gamestate немає кореневого clusters= — не можу вставити блок achievement")
    return gamestate[: clusters.start()] + _achievement_block() + gamestate[clusters.start() :]


def restore_achievement_eligibility(gamestate: bytes) -> bytes:
    """Clear the console-used flag and restore the root achievement ID list."""
    return _ensure_achievement_block(_set_cheated_on_save(gamestate, cheated=False))


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(filename=name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 0
    info.create_version = 63
    info.extract_version = 20
    info.flag_bits = 0
    info.external_attr = 0
    return info


def write_save(path: Path, files: dict[str, bytes]) -> None:
    if path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        (path / "gamestate").write_bytes(files["gamestate"])
        (path / "meta").write_bytes(files["meta"])
        return
    write_sav(path, files)


def write_sav(path: Path, files: dict[str, bytes]) -> None:
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=False) as archive:
            for name in ("gamestate", "meta"):
                archive.writestr(_zip_info(name), files[name])
        tmp_path.replace(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def desktop_dir() -> Path:
    return Path.home() / "Desktop"


def _desktop_copy_name(path: Path) -> str:
    campaign = path.parent.name
    slot = _slot_name(path)
    if path.is_dir():
        return f"{campaign}_{slot}"
    return f"{campaign}_{slot}{path.suffix}"


def copy_save_to_desktop(path: Path) -> Path:
    desktop = desktop_dir()
    if not desktop.is_dir():
        raise FileNotFoundError(f"Немає папки Desktop: {desktop}")

    dest = desktop / _desktop_copy_name(path)
    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if path.is_dir():
            dest = desktop / f"{dest.name}_{stamp}"
        else:
            dest = desktop / f"{dest.stem}_{stamp}{dest.suffix}"

    if path.is_dir():
        shutil.copytree(path, dest)
    else:
        shutil.copy2(path, dest)
    return dest


def backup_save(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = path.parent / "ironman_backups"
    backup_dir.mkdir(exist_ok=True)
    if path.is_dir():
        backup_path = backup_dir / f"{path.name}.{stamp}"
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(path, backup_path)
        return backup_path
    backup_path = backup_dir / f"{path.stem}.{stamp}.sav"
    shutil.copy2(path, backup_path)
    return backup_path


def _ironman_target(path: Path) -> Path:
    campaign = path.parent
    sav = campaign / "ironman.sav"
    folder = campaign / "ironman"
    if folder.is_dir() and not sav.exists():
        return folder
    if folder.is_dir() and sav.exists():
        if _save_modified(folder) > sav.stat().st_mtime:
            return folder
    return sav


def convert_save(path: Path, enable_ironman: bool) -> tuple[Path, Path]:
    files = _read_save_files(path)
    currently_ironman = _is_ironman(files)
    currently_cheated = _is_cheated(files["gamestate"])
    need_ironman = currently_ironman != enable_ironman
    need_restore = enable_ironman and (not currently_ironman or currently_cheated)
    if not need_ironman and not need_restore:
        if enable_ironman:
            raise ValueError("Цей сейв уже Ironman і без позначки читів.")
        raise ValueError("Цей сейв уже звичайний.")

    if need_ironman:
        files["gamestate"] = _set_gamestate_ironman(files["gamestate"], enable_ironman)
        files["meta"] = _set_meta_ironman(files["meta"], enable_ironman)
    if need_restore:
        files["gamestate"] = restore_achievement_eligibility(files["gamestate"])

    backup_path = backup_save(path)
    target = path
    if enable_ironman and _slot_name(path) != "ironman":
        target = _ironman_target(path)
        if target.exists() and target.resolve() != path.resolve():
            backup_save(target)

    write_save(target, files)
    return target, backup_path


def latest_save(saves: list[SaveInfo] | None = None) -> SaveInfo:
    items = saves if saves is not None else find_saves()
    if not items:
        raise FileNotFoundError(
            "Не знайшов сейви Stellaris.\n"
            "Очікувана папка: Documents/Paradox Interactive/Stellaris/save games"
        )
    return items[0]


def format_save(save: SaveInfo) -> str:
    mode = "Ironman" if save.ironman else "звичайний"
    if save.cheated:
        mode += " · ачівки заблоковані (консоль)"
    return (
        f"{save.empire}  |  {save.date}  |  {mode}\n"
        f"{save.path}\n"
        f"змінено: {save.modified.strftime('%Y-%m-%d %H:%M:%S')}"
    )
