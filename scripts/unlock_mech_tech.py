"""Unlock mecha techs and infinite upgrades in any DSP save file.

Usage:
    python3 unlock_mech_tech.py <input.dsv> [options]

Examples:
    # Default: unlock everything, output to _<input_name>_.dsv in same dir
    python3 unlock_mech_tech.py /path/to/my_save.dsv

    # Only unlock techs, skip infinite upgrades
    python3 unlock_mech_tech.py /path/to/my_save.dsv --no-infinite

    # Only boost mecha stats, no tech tree changes
    python3 unlock_mech_tech.py /path/to/my_save.dsv --no-tech --no-infinite

    # Set infinite techs to a safer level (LV100 instead of LV5001)
    python3 unlock_mech_tech.py /path/to/my_save.dsv --infinite-level 100

    # Specify custom output path
    python3 unlock_mech_tech.py /path/to/my_save.dsv -o /path/to/_modified_.dsv

Output:
    By default writes to _<basename>_.dsv in the same directory as the input.
    Example: input "MyGame.dsv" -> output "_MyGame_.dsv"

    The output filename follows DSP's required _name_.dsv convention.
"""
import argparse, os, sys, io, importlib.util, struct


# ============================================================================
# Setup: load the parser
# ============================================================================
REPO = '/home/z/my-project/dsp_save_parser'
sys.path.insert(0, REPO)

# Regenerate parser to ensure save_format.txt changes are picked up
spec = importlib.util.spec_from_file_location('gen', os.path.join(REPO, 'dsp_save_parser', 'generator.py'))
gen_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen_mod)
GEN_PATH = os.path.join(REPO, 'dsp_save_parser', 'save_format_generated.py')
FMT_PATH = os.path.join(REPO, 'dsp_save_parser', 'save_format.txt')
if os.path.exists(GEN_PATH):
    os.remove(GEN_PATH)
gen_mod.generate_parser(FMT_PATH, GEN_PATH)

import dsp_save_parser
spec2 = importlib.util.spec_from_file_location('dsp_save_parser.save_format_generated', GEN_PATH)
sfmt = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(sfmt)


# ============================================================================
# Tech IDs known to be mecha-related (from DSP's data tables).
# These are just some of the well-known ones — you can extend this list.
# Full list: see GameHistoryData.techState[].id from any save.
# ============================================================================
MECHA_TECH_IDS = {
    # Core / power (1000-1199)
    1001: 'Mecha Core LV2',
    1002: 'Mecha Core LV3',
    1003: 'Mecha Core LV4',
    1004: 'Mecha Core LV5',
    1101: 'Mecha Engine LV2',
    1102: 'Mecha Engine LV3',
    1103: 'Mecha Engine LV4',
    1104: 'Mecha Engine LV5',
    1111: 'Plasma Thrust',
    1112: 'Antimatter Sail',
    1113: 'Warp Drive',
    1114: 'Mission Engine',
    # Mining / fabrication (1200-1299)
    1201: 'Mining LV2',
    1202: 'Mining LV3',
    1203: 'Mining LV4',
    1204: 'Mining LV5',
    1211: 'Replication LV2',
    1212: 'Replication LV3',
    1213: 'Replication LV4',
    1214: 'Replication LV5',
    # Combat / shield (1300-1399)
    1301: 'Energy Shield',
    1302: 'Energy Shield LV2',
    1303: 'Energy Shield LV3',
    1304: 'Energy Shield LV4',
    1305: 'Energy Shield LV5',
    1310: 'Energy Shield Burst',
    # Construction (1400-1499)
    1401: 'Construction Drone LV2',
    1402: 'Construction Drone LV3',
    1403: 'Construction Drone LV4',
    1404: 'Construction Drone LV5',
    1411: 'Build Area LV2',
    1412: 'Build Area LV3',
    1413: 'Build Area LV4',
    1414: 'Build Area LV5',
    # Vein Utilization + Mining (1500-1599)
    1501: 'Vein Utilization LV1',
    1502: 'Vein Utilization LV2',
    1503: 'Vein Utilization LV3',
    1504: 'Vein Utilization LV4',
    1505: 'Vein Utilization LV5',
    1506: 'Vein Utilization LV6',
    1507: 'Vein Utilization LV7',
    1508: 'Vein Utilization LV8',
    1509: 'Vein Utilization LV9',
    1511: 'Miner LV1',
    1512: 'Miner LV2',
    1513: 'Miner LV3',
    1521: 'Long-distance Mining LV1',
    1522: 'Long-distance Mining LV2',
    1523: 'Long-distance Mining LV3',
    # Logistic Drones (1600-1699)
    1601: 'Logistic Drone LV2',
    1602: 'Logistic Drone LV3',
    1603: 'Logistic Drone LV4',
    1604: 'Logistic Drone LV5',
    1605: 'Logistic Drone LV6',
    1606: 'Logistic Drone LV7',
    1607: 'Logistic Drone LV8',
    1608: 'Logistic Drone LV9',
    # Logistic Ships (1700-1799)
    1701: 'Logistic Ship LV2',
    1702: 'Logistic Ship LV3',
    1703: 'Logistic Ship LV4',
    1704: 'Logistic Ship LV5',
    1705: 'Logistic Ship LV6',
}


# ============================================================================
# Modification functions
# ============================================================================

def unlock_mecha_tech(game_save):
    """Set unlocked=True on every tech whose id is in MECHA_TECH_IDS."""
    history = game_save.game_data.history
    tech_states = history.tech_state
    unlocked_count = 0
    skipped_count = 0
    for tech in tech_states:
        if tech.id in MECHA_TECH_IDS:
            if not tech.unlocked:
                tech.unlocked = True
                tech.cur_level = tech.max_level if tech.max_level > 0 else 1
                print(f'  Unlocked tech {tech.id} ({MECHA_TECH_IDS[tech.id]}): '
                      f'cur={tech.cur_level}/{tech.max_level}')
                unlocked_count += 1
            else:
                skipped_count += 1
    print(f'\nTech tree: unlocked {unlocked_count} new techs, '
          f'{skipped_count} already unlocked (out of {len(tech_states)} total techs).')
    return unlocked_count


def unlock_infinite_upgrades(game_save, target_level=5001):
    """Set all infinite techs (max_level >= 100) to cur_level = min(target_level, max_level)."""
    history = game_save.game_data.history
    tech_states = history.tech_state
    infinite_techs = [t for t in tech_states if t.max_level >= 100]
    print(f'Found {len(infinite_techs)} infinite upgrade techs '
          f'(max_level >= 100). Setting each to cur_level={target_level} '
          f'(or max_level if smaller):')
    for tech in infinite_techs:
        target = min(target_level, tech.max_level)
        old_cur = tech.cur_level
        tech.unlocked = True
        tech.cur_level = target
        print(f'  tech {tech.id}: cur_level {old_cur} -> {tech.cur_level} '
              f'(max={tech.max_level})')
    print(f'\nInfinite upgrades: set {len(infinite_techs)} techs to level {target_level}.')
    return len(infinite_techs)


def boost_mecha_stats(player):
    """Directly set mecha stats to maxed values, bypassing the tech tree."""
    mecha = player.mecha

    # Mecha levels
    mecha.core_level = 5
    mecha.thrust_level = 5

    # Speeds
    mecha.mining_speed = 5.0
    mecha.replicate_speed = 5.0
    mecha.walk_speed = 12.0
    mecha.jump_speed = 25.0
    mecha.max_sail_speed = 600.0
    mecha.max_warp_speed = 60000.0
    mecha.build_area = 40.0

    # HP / shield
    mecha.hp_max = 5000
    mecha.hp_max_upgrade = 5000
    mecha.hp_recover = 500
    mecha.hp = mecha.hp_max
    mecha.energy_shield_unlocked = True
    mecha.energy_shield_recharge_enabled = True
    mecha.energy_shield_recharge_speed = 100.0
    mecha.energy_shield_radius = 30.0
    mecha.energy_shield_capacity = 10000
    mecha.energy_shield_energy = mecha.energy_shield_capacity

    # Energy
    mecha.core_energy = mecha.core_energy_cap
    mecha.reactor_energy = 1e9

    print(f'  Mecha stats boosted:')
    print(f'    core_level={mecha.core_level}, thrust_level={mecha.thrust_level}')
    print(f'    mining_speed={mecha.mining_speed}, max_warp_speed={mecha.max_warp_speed}')
    print(f'    hp={mecha.hp}/{mecha.hp_max}, energy_shield_unlocked={mecha.energy_shield_unlocked}')


# ============================================================================
# Save output with fileLength fix
# ============================================================================

def save_with_corrected_file_length(save, output_path):
    """Save the game save to output_path, ensuring fileLength matches actual size.

    The parser's len() undercounts by ~10 bytes (a known quirk), so we save
    to a buffer first to determine the actual byte count, then set
    file_length to match, then re-save and write to disk.
    """
    # First pass: save to buffer to find actual byte count
    buf = io.BytesIO()
    save.save(buf)
    actual_size = buf.tell()

    # If file_length doesn't match actual output size, fix it and re-save
    if save.file_length != actual_size:
        print(f'  Adjusting file_length: {save.file_length} -> {actual_size}')
        save.file_length = actual_size
        buf = io.BytesIO()
        save.save(buf)

    # Write to disk
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(buf.getvalue())

    return actual_size


# ============================================================================
# Output filename helper
# ============================================================================

def make_output_path(input_path, output_arg=None):
    """Generate output path that follows DSP's _name_.dsv convention."""
    if output_arg:
        return output_arg
    dirname = os.path.dirname(os.path.abspath(input_path))
    basename = os.path.basename(input_path)
    # Strip .dsv extension and any leading/trailing underscores
    name = basename
    if name.endswith('.dsv'):
        name = name[:-4]
    name = name.strip('_')
    return os.path.join(dirname, f'_{name}_.dsv')


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Unlock mecha techs and infinite upgrades in a DSP save file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  # Default: unlock everything
  python3 unlock_mech_tech.py /path/to/my_save.dsv

  # Only unlock techs, skip infinite upgrades
  python3 unlock_mech_tech.py /path/to/my_save.dsv --no-infinite

  # Set infinite techs to LV100 (safer than default 5001)
  python3 unlock_mech_tech.py /path/to/my_save.dsv --infinite-level 100

  # Custom output path
  python3 unlock_mech_tech.py /path/to/my_save.dsv -o /path/to/_modified_.dsv
''')
    parser.add_argument('input', help='Path to input .dsv save file')
    parser.add_argument('-o', '--output', help='Output path (default: _<name>_.dsv in input dir)',
                        default=None)
    parser.add_argument('--no-tech', action='store_true',
                        help='Skip unlocking finite mecha techs')
    parser.add_argument('--no-infinite', action='store_true',
                        help='Skip setting infinite upgrade techs')
    parser.add_argument('--no-mecha', action='store_true',
                        help='Skip boosting mecha stats directly')
    parser.add_argument('--infinite-level', type=int, default=5001,
                        help='Target level for infinite upgrades (default: 5001)')
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f'ERROR: Input file not found: {input_path}')
        sys.exit(1)
    output_path = make_output_path(input_path, args.output)

    print(f'Input:  {input_path}')
    print(f'Output: {output_path}')
    print()

    # === Parse ===
    print(f'Parsing {input_path}...')
    with open(input_path, 'rb') as f:
        save = sfmt.GameSave.parse(f)
    print(f'  Original file_length: {save.file_length}')

    # === Step 1: Unlock finite mecha techs ===
    if not args.no_tech:
        print('\n=== Step 1: Unlock mecha techs in tech tree ===')
        unlock_mecha_tech(save)
    else:
        print('\n=== Step 1: SKIPPED (--no-tech) ===')

    # === Step 2: Set infinite upgrade techs ===
    if not args.no_infinite:
        print(f'\n=== Step 2: Set all infinite upgrade techs to level {args.infinite_level} ===')
        unlock_infinite_upgrades(save, target_level=args.infinite_level)
    else:
        print('\n=== Step 2: SKIPPED (--no-infinite) ===')

    # === Step 3: Boost mecha stats ===
    if not args.no_mecha:
        print('\n=== Step 3: Boost mecha stats directly ===')
        boost_mecha_stats(save.game_data.main_player)
    else:
        print('\n=== Step 3: SKIPPED (--no-mecha) ===')

    # === Save with fileLength fix ===
    print('\n=== Saving ===')
    actual_size = save_with_corrected_file_length(save, output_path)

    # === Verify ===
    print(f'\nSaved modified save to: {output_path}')
    print(f'  Original size: {os.path.getsize(input_path)} bytes')
    print(f'  New size:      {os.path.getsize(output_path)} bytes')

    # Validate
    print('\n=== Validating output ===')
    with open(output_path, 'rb') as f:
        data = f.read(60)
    magic = data[:6]
    file_length = struct.unpack('<q', data[6:14])[0]
    actual_file_size = os.path.getsize(output_path)

    checks_ok = True
    if magic == b'VFSAVE':
        print(f'  [OK] Magic: {magic}')
    else:
        print(f'  [FAIL] Magic: {magic!r}')
        checks_ok = False
    if file_length == actual_file_size:
        print(f'  [OK] fileLength ({file_length}) == file size ({actual_file_size})')
    else:
        print(f'  [FAIL] fileLength ({file_length}) != file size ({actual_file_size})')
        checks_ok = False
    basename = os.path.basename(output_path)
    if basename.startswith('_') and basename.endswith('_.dsv'):
        print(f'  [OK] Filename follows _name_.dsv convention')
    else:
        print(f'  [WARN] Filename "{basename}" should be _name_.dsv for DSP to recognize it')

    # Re-parse to verify structural integrity
    print('\nVerifying: re-parsing the new save...')
    with open(output_path, 'rb') as f:
        sfmt.GameSave.parse(f)
    print('  Re-parse OK! Save is structurally valid.')

    if checks_ok:
        print(f'\n=== DONE ===')
        print(f'Copy "{output_path}" to your DSP save folder:')
        print(f'  Windows: C:\\Users\\<you>\\Documents\\Dyson Sphere Program\\Save\\')
    else:
        print(f'\n=== DONE WITH WARNINGS ===')


if __name__ == '__main__':
    main()
