#!/usr/bin/env python3
"""
MAP-Elites tooling for Mechanical Reverie.

The map (elites-map.json) holds the best-known SCORE for every behavioral niche
the engine can occupy. Cells: flowCharacter x mechanicalCharacter x ground register.

Commands:
  python3 map_tools.py seed                      # (re)seed from selected-genomes.json — idempotent
  python3 map_tools.py challenge FILE [--source LABEL]
                                                 # challenge cells with candidate genomes
  python3 map_tools.py status                    # coverage grid + gaps + recent challenges
  python3 map_tools.py frontier [--mode cartographer|challenger] [--cell KEY] [--commit]
                                                 # pick next frontier-day target (dry-run unless --commit)

Doctrine:
  - Cells hold scores (genome + seeds + paletteColors), per canonical-seeds v3.0.0.
  - Archive seeding replaces an incumbent on plain fitness improvement (>).
  - External candidates must beat the incumbent by >= CHALLENGE_MARGIN.
  - Curatorial override remains sovereign for daily published pieces; the map is
    the engine's long-term self-knowledge, not the day's selector.
"""

import json
import sys
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
GENOMES_PATH = os.path.join(HERE, 'selected-genomes.json')
MAP_PATH = os.path.join(HERE, 'elites-map.json')

FLOWS = ['transit', 'biological', 'vortex', 'mathematical', 'dispersal', 'oscilloscope']
MECHS = ['gear', 'circuit', 'plotter', 'led']
GROUNDS = ['light', 'dark']
CHALLENGE_MARGIN = 0.05
LOG_CAP = 300


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def classify(genome):
    """Return cell key 'flow|mech|ground' or None if unclassifiable."""
    fc = genome.get('flowCharacter')
    mc = genome.get('mechanicalCharacter')
    if not fc or not mc:
        return None
    ground = 'dark' if (genome.get('bgDarkness') or 0) > 0.5 else 'light'
    return f'{fc}|{mc}|{ground}'


def load_map():
    if os.path.exists(MAP_PATH):
        with open(MAP_PATH) as f:
            m = json.load(f)
    else:
        m = {'version': 1, 'axes': {'flow': list(FLOWS), 'mech': list(MECHS), 'ground': list(GROUNDS)},
             'challengeMargin': CHALLENGE_MARGIN, 'updated': None, 'cells': {}, 'challengeLog': []}
    return m


def save_map(m):
    m['updated'] = now_iso()
    m['challengeLog'] = m['challengeLog'][-LOG_CAP:]
    with open(MAP_PATH, 'w') as f:
        json.dump(m, f, indent=2, ensure_ascii=False)


def extend_axes(m, cell_key):
    """Unknown future characters auto-extend the axes rather than erroring."""
    fc, mc, _ = cell_key.split('|')
    if fc not in m['axes']['flow']:
        m['axes']['flow'].append(fc)
    if mc not in m['axes']['mech']:
        m['axes']['mech'].append(mc)


def log_challenge(m, cell, challenger_fit, incumbent_fit, result, source):
    m['challengeLog'].append({
        'ts': now_iso(), 'cell': cell,
        'challengerFitness': round(challenger_fit, 4) if challenger_fit is not None else None,
        'incumbentFitness': round(incumbent_fit, 4) if incumbent_fit is not None else None,
        'result': result, 'source': source,
    })


def cmd_seed():
    with open(GENOMES_PATH) as f:
        data = json.load(f)
    m = load_map()
    placed = replaced = skipped = 0
    for i, e in enumerate(data):
        g = e.get('genome') or {}
        cell = classify(g)
        fit = e.get('fitness')
        if cell is None or fit is None:
            skipped += 1
            continue
        extend_axes(m, cell)
        prov = {'type': 'frontier' if e.get('frontier') else 'archive-winner',
                'gen': i + 1, 'day': e.get('day'),
                'date': e.get('date'), 'title': e.get('title'), 'filename': e.get('filename')}
        if e.get('frontier'):
            prov['cell'] = e.get('cell')
            prov['frontierIndex'] = e.get('frontierIndex')
        incumbent = m['cells'].get(cell)
        # Idempotency: an archive entry that IS the incumbent refreshes itself in place.
        if incumbent and incumbent.get('provenance', {}).get('gen') == i + 1:
            incumbent.update({'fitness': fit, 'genome': g, 'provenance': prov})
            continue
        if incumbent is None:
            m['cells'][cell] = {'fitness': fit, 'genome': g, 'provenance': prov, 'since': now_iso()}
            log_challenge(m, cell, fit, None, 'placed-empty', f'seed gen {i+1}')
            placed += 1
        elif fit > incumbent['fitness']:
            log_challenge(m, cell, fit, incumbent['fitness'], 'dethroned', f'seed gen {i+1}')
            m['cells'][cell] = {'fitness': fit, 'genome': g, 'provenance': prov, 'since': now_iso()}
            replaced += 1
    save_map(m)
    total = len(m['axes']['flow']) * len(m['axes']['mech']) * len(m['axes']['ground'])
    print(f'Seed complete: {placed} placed, {replaced} dethroned, {skipped} unclassifiable/unscored.')
    print(f'Coverage: {len(m["cells"])}/{total} cells.')


def cmd_challenge(path, source):
    with open(path) as f:
        payload = json.load(f)
    candidates = payload.get('candidates', payload) if isinstance(payload, dict) else payload
    m = load_map()
    won = lost = invalid = 0
    for c in candidates:
        g = c.get('genome') or {}
        fit = c.get('fitness')
        cell = classify(g)
        if cell is None or fit is None:
            invalid += 1
            continue
        extend_axes(m, cell)
        incumbent = m['cells'].get(cell)
        prov = {'type': 'candidate', 'source': source, 'day': c.get('day'), 'date': c.get('date')}
        if incumbent is None:
            m['cells'][cell] = {'fitness': fit, 'genome': g, 'provenance': prov, 'since': now_iso()}
            log_challenge(m, cell, fit, None, 'placed-empty', source)
            won += 1
        elif fit >= incumbent['fitness'] + m.get('challengeMargin', CHALLENGE_MARGIN):
            log_challenge(m, cell, fit, incumbent['fitness'], 'dethroned', source)
            m['cells'][cell] = {'fitness': fit, 'genome': g, 'provenance': prov, 'since': now_iso()}
            won += 1
        else:
            log_challenge(m, cell, fit, incumbent['fitness'], 'held', source)
            lost += 1
    save_map(m)
    print(f'Challenge complete ({source}): {won} cells taken, {lost} held by incumbents, {invalid} invalid.')


def cmd_frontier(mode=None, cell=None, commit=False):
    """Pick the next frontier-day target. Dry-run unless --commit.

    cartographer: attack the emptiest region — the empty cell whose flow-row and
                  mech-column contain the fewest filled cells (deterministic tie-break).
    challenger:   attack the staleness — the filled cell whose elite has held its
                  seat the longest (oldest `since`).
    Modes alternate automatically across committed picks; --mode or --cell override.
    """
    m = load_map()
    flows, mechs, grounds = m['axes']['flow'], m['axes']['mech'], m['axes']['ground']
    all_keys = [f'{f}|{mc}|{gr}' for f in flows for mc in mechs for gr in grounds]
    empty = [k for k in all_keys if k not in m['cells']]
    state = m.setdefault('frontierState', {'lastMode': None, 'history': []})

    if cell:
        if cell not in all_keys:
            sys.exit(f'unknown cell: {cell}')
        target, chosen_mode = cell, ('challenger' if cell in m['cells'] else 'cartographer')
        picked_by = 'manual'
    else:
        if mode is None:
            mode = 'challenger' if state.get('lastMode') == 'cartographer' else 'cartographer'
        if mode == 'cartographer' and not empty:
            mode = 'challenger'  # map fully covered — nothing to chart
        if mode == 'cartographer':
            def emptiness(k):
                f_, mc_, _ = k.split('|')
                row = sum(1 for kk in m['cells'] if kk.split('|')[0] == f_)
                col = sum(1 for kk in m['cells'] if kk.split('|')[1] == mc_)
                return (row + col, all_keys.index(k))
            target = min(empty, key=emptiness)
        else:
            target = min(m['cells'].items(), key=lambda kv: kv[1].get('since') or '')[0]
        chosen_mode, picked_by = mode, 'auto'

    incumbent = m['cells'].get(target)
    out = {
        'mode': chosen_mode, 'pickedBy': picked_by, 'cell': target,
        'ground': target.split('|')[2],
        'incumbent': None if incumbent is None else {
            'fitness': incumbent['fitness'],
            'since': incumbent.get('since'),
            'provenance': incumbent.get('provenance'),
            'beatBy': round(incumbent['fitness'] + m.get('challengeMargin', CHALLENGE_MARGIN), 4),
        },
        'committed': bool(commit),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if incumbent is None:
        print(f'\n→ empty cell: any certified candidate takes it.')
    else:
        print(f'\n→ challenger must reach fitness ≥ {out["incumbent"]["beatBy"]} to dethrone.')
    if commit:
        state['lastMode'] = chosen_mode
        state['history'] = (state.get('history') or [])[-49:] + [
            {'ts': now_iso(), 'mode': chosen_mode, 'cell': target, 'pickedBy': picked_by}]
        save_map(m)
        print('→ pick committed to frontierState.')


def cmd_status():
    m = load_map()
    cells = m['cells']
    flows, mechs = m['axes']['flow'], m['axes']['mech']
    for gr in m['axes']['ground']:
        print(f'--- {gr} ground ---')
        for f_ in flows:
            row = []
            for mc in mechs:
                e = cells.get(f'{f_}|{mc}|{gr}')
                row.append(f'{mc}:{e["fitness"]:.2f}' if e else f'{mc}:·')
            print(f'  {f_:14s} ' + '  '.join(row))
    total = len(flows) * len(mechs) * len(m['axes']['ground'])
    print(f'\nFilled: {len(cells)}/{total}')
    empty = [k for f_ in flows for mc in mechs for gr in m['axes']['ground']
             if (k := f'{f_}|{mc}|{gr}') not in cells]
    print(f'Frontier ({len(empty)} empty): ' + ', '.join(empty[:12]) + (' …' if len(empty) > 12 else ''))
    if m['challengeLog']:
        print('\nRecent challenges:')
        for c in m['challengeLog'][-5:]:
            print(f'  {c["ts"]} {c["cell"]:34s} {c["result"]:12s} ({c["source"]})')


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] == 'status':
        cmd_status() if os.path.exists(MAP_PATH) else print('No map yet — run: python3 map_tools.py seed')
    elif args[0] == 'seed':
        cmd_seed()
    elif args[0] == 'challenge':
        if len(args) < 2:
            sys.exit('usage: map_tools.py challenge FILE [--source LABEL]')
        src = args[args.index('--source') + 1] if '--source' in args else os.path.basename(args[1])
        cmd_challenge(args[1], src)
    elif args[0] == 'frontier':
        mode = args[args.index('--mode') + 1] if '--mode' in args else None
        cell = args[args.index('--cell') + 1] if '--cell' in args else None
        if mode not in (None, 'cartographer', 'challenger'):
            sys.exit('--mode must be cartographer or challenger')
        cmd_frontier(mode=mode, cell=cell, commit='--commit' in args)
    else:
        sys.exit(__doc__)
