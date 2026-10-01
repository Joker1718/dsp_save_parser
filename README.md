# DSP Save Toolkit

Tools for modifying Dyson Sphere Program save files (.dsv) on game version 0.10.35.29104.

## Quick start

```bash
# Unlock all mecha techs + set infinite upgrades to LV5001 + boost mecha stats
python3 scripts/unlock_mech_tech.py /path/to/your_save.dsv

# This creates _<your_save_name>_.dsv in the same folder.
# Copy that file to your DSP save folder:
#   Windows: C:\Users\<you>\Documents\Dyson Sphere Program\Save\
```

## Scripts

### `unlock_mech_tech.py` — Main modification tool

Modifies a DSP save file to unlock mecha techs, set infinite upgrades, and boost mecha stats.

```bash
# Full unlock (default)
python3 scripts/unlock_mech_tech.py /path/to/save.dsv

# Only unlock finite techs, skip infinite upgrades and mecha stat boost
python3 scripts/unlock_mech_tech.py /path/to/save.dsv --no-infinite --no-mecha

# Set infinite techs to a safer LV100 instead of LV5001
python3 scripts/unlock_mech_tech.py /path/to/save.dsv --infinite-level 100

# Custom output path
python3 scripts/unlock_mech_tech.py /path/to/save.dsv -o /path/to/_modified_.dsv
```

**What it does:**
- **Step 1**: Unlocks 52 mecha-related finite techs (Core, Engine, Mining, Shield, Vein Utilization LV1-9, Logistic Drones LV2-9, etc.)
- **Step 2**: Sets all 13 infinite upgrade techs to LV5001 (or custom level)
- **Step 3**: Boosts mecha stats directly (HP 5000, mining 5x, warp 60000, shield unlocked)
- Automatically fixes `fileLength` to match actual file size (critical for DSP to load the save)
- Auto-names output as `_<name>_.dsv` (DSP convention)
- Validates output and re-parses to verify structural integrity

### `validate_save.py` — Diagnostic tool

Checks a .dsv file for common issues that cause "invalid save file" errors.

```bash
python3 scripts/validate_save.py /path/to/save.dsv
```

Checks:
- Magic bytes (`VFSAVE`)
- `fileLength` matches actual file size
- Game version
- PNG screenshot present
- File naming convention (`_name_.dsv`)

### `list_techs.py` — Tech inspector

Lists all techs in a save file with their unlock status and levels.

```bash
python3 scripts/list_techs.py  # hardcoded to Indot.dsv — edit to use your save
```

### `list_infinite_techs.py` — Infinite tech inspector

Lists only the infinite upgrade techs (max_level >= 100) in a save.

```bash
python3 scripts/list_infinite_techs.py  # hardcoded to Indot.dsv — edit to use your save
```

## Requirements

- Python 3.8+
- The `dsp_save_parser/` package included in this toolkit (already patched for 0.10.35.29104)

## How it works

The script:
1. Loads the `dsp_save_parser` package (auto-regenerates the parser from `save_format.txt`)
2. Parses the input `.dsv` file into a Python object tree
3. Modifies the `GameHistoryData.tech_state[]` array (sets `unlocked=True`, `cur_level=max_level` for finite techs, `cur_level=5001` for infinite techs)
4. Modifies `Player.mecha` fields directly (HP, speed, shield, etc.)
5. Saves to a new `.dsv` file with corrected `fileLength`

The original save file is never modified.

## Troubleshooting

### "Invalid save file" error in DSP

Run `validate_save.py` on your output file:
```bash
python3 scripts/validate_save.py _your_save_.dsv
```

Common issues:
- `fileLength` mismatch → re-run `unlock_mech_tech.py` (it auto-fixes this)
- Wrong filename → must be `_<name>_.dsv` (script auto-names correctly by default)

### Save loads but techs don't show as unlocked

DSP may need the `hashUploaded` field to be ≥ `hashNeeded` for some techs. If the unlock doesn't take effect, try also boosting `hashUploaded`:
```python
# In unlock_mech_tech.py, in unlock_mecha_tech(), add:
tech.hash_uploaded = tech.hash_needed
```

### Game crashes on load

The LV5001 setting may be too aggressive for some infinite techs. Try a safer level:
```bash
python3 scripts/unlock_mech_tech.py /path/to/save.dsv --infinite-level 100
```

## Files

```
dsp_save_toolkit/
├── README.md                          (this file)
├── dsp_save_parser/                   (the parser package, patched for 0.10.35.29104)
│   ├── dsp_save_parser/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── generator.py
│   │   ├── save_format.txt            (the format definition)
│   │   └── blueprint_format.txt
│   ├── main.py                        (basic parser demo)
│   ├── blueprint.py
│   └── buggy_md5.py                   (DSP's non-standard MD5 implementation)
└── scripts/
    ├── unlock_mech_tech.py            (main modification tool)
    ├── validate_save.py               (diagnostic tool)
    ├── list_techs.py                  (tech inspector)
    └── list_infinite_techs.py         (infinite tech inspector)
```
