"""Identify the infinite upgrade techs in Indot.dsv.

In DSP, "infinite upgrades" are techs that can be researched forever — they
use Universe Matrix as input and have max_level set to 10000 in the save file.
These appear in the 5000-6199 ID range.

Known DSP infinite upgrades (from game data):
  5001-5006: Logistics Drone Engine (drone speed)
  5101-5106: Logistics Ship Engine (ship sail/warp speed)
  5201-5206: Vessel Tank (logistic capacity)
  5301-5305: Mining Speed (infinite)
  5401-5405: Replicator Speed (infinite)
  5601-5605: Mecha Core Power (infinite)
  5701-5705: Mecha Engine (sail speed infinite)
  5801-5807: Combat / Damage
  5901-5907: Combat / Durability
  6001-6006: Combat / Damage Scale
  6101-6106: Combat / Misc

Setting cur_level=5001 on these will give a massive bonus (DSP caps display
at 60 but the underlying value is unbounded).
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

techs = save.game_data.history.tech_state
print('=== Infinite upgrade techs (max_level >= 100) ===')
print(f'{"id":<8}{"unlocked":<10}{"cur":<8}{"max":<8}')
infinite_techs = []
for t in techs:
    if t.max_level >= 100 or t.id >= 5000:
        infinite_techs.append(t)
        flag = '✓' if t.unlocked else ' '
        print(f'{t.id:<8}{flag:<10}{t.cur_level:<8}{t.max_level:<8}')
print(f'\nTotal infinite upgrade techs: {len(infinite_techs)}')
