#!/usr/bin/env python3
"""Generate per-trait run files for the configured species id (default 357)."""

from __future__ import annotations

import sys

from run_scripts import DEFAULT_SPECIES_ID, get_species_id, rewrite_pop_trait_files


def main() -> None:
    species_id = sys.argv[1] if len(sys.argv) > 1 else get_species_id() or DEFAULT_SPECIES_ID
    count = rewrite_pop_trait_files(species_id)
    print(f"species {species_id}: wrote {count} files")


if __name__ == "__main__":
    main()
