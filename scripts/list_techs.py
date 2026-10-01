"""Search the tech list in Indot.dsv for any techs whose name (when looked up
in the DSP tech prototypes) contains "Vein", "Utilization", "Mining", "Extraction",
or related terms. Since the parser doesn't ship with the game's TechProto table,
we just list all tech IDs present in the save so we can identify the vein ones
by pattern (they're typically in the 1400-1499 or 2400-2499 range).
"""
import os, sys, importlib.util

REPO = '/home/z/my-project/dsp_save_parser'
sys.path.insert(0, REPO)
SAVE = os.path.join(REPO, 'Indot.dsv')

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

with open(SAVE, 'rb') as f:
    save = sfmt.GameSave.parse(f)

tech_states = save.game_data.history.tech_state
print(f'Total techs in save: {len(tech_states)}')
print()
print('All tech IDs (sorted):')
print(sorted(t.id for t in tech_states))
print()
print('Techs grouped by ID prefix (first 2 digits):')
from collections import defaultdict
groups = defaultdict(list)
for t in tech_states:
    prefix = t.id // 100
    groups[prefix].append((t.id, t.unlocked, t.cur_level, t.max_level))
for prefix in sorted(groups):
    techs = groups[prefix]
    print(f'  {prefix*100}-{prefix*100+99}: {len(techs)} techs')
    for tid, unlocked, cur, mx in techs:
        flag = '✓' if unlocked else ' '
        print(f'    [{flag}] id={tid}  cur={cur}  max={mx}')
