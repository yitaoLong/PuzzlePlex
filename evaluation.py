import argparse
import os
import json
from collections import defaultdict
import random
import numpy as np
from scipy import stats

# -------- configuration --------

SINGLE_DET = [
    "TidyTowerPuzzle", "OptimalTouringPuzzle", "CountMaximalCocktailsPuzzle",
]
SINGLE_STO = [
    "RubyRisksPuzzle", "ExclusivityProbesPuzzle", "MaxTargetPuzzle",
]
TWO_DET = [
    "CardNimPuzzle", "SudoKillPuzzle", "MaxMaximalCocktailsPuzzle",
    "ExclusivityParticlesPuzzle", "SuperplyPuzzle",
]
TWO_STO = [
    "BeatOrBombStoPuzzle", "LargerTargetPuzzle",
]
TWO_DET_IMAGE = ["SudoKillMPuzzle", "SuperplyMPuzzle"]

CODE_MODELS = [
    "custom", "gpt-4.1", "o4-mini", "gemini-2.5-pro-preview-03-25",
    "grok-3-mini-beta", "deepseek-reasoner", "deepseek-chat",
    "phi-4-multimodal-instruct", "qwq", "llama", "gemma", "qwen",
]

REASONING_MODELS = [
    "o4-mini", "gemini-2.5-pro-preview-03-25",
    "grok-3-mini-beta", "deepseek-reasoner",  "qwq",
]
K_ELO = 32

# -------- utilities --------

def parse_args():
    p = argparse.ArgumentParser(description="Evaluate puzzle results (normalized vs. Elo)")
    p.add_argument("--data_dir", help="Directory of JSON result files")
    p.add_argument("--eval-type", choices=["instruction", "code"], required=True,
                   help="'instruction' or 'code' evaluation")
    p.add_argument("--score-type", choices=["normalized score", "elo score"],
                   required=True, help="Which scoring to compute")
    return p.parse_args()


def list_puzzles(eval_type):
    if eval_type == "instruction":
        return SINGLE_DET + TWO_DET + TWO_DET_IMAGE
    else:
        return SINGLE_DET + SINGLE_STO + TWO_DET + TWO_STO


def load_all(data_dir, puzzles):
    out = {}
    for name in puzzles:
        with open(os.path.join(data_dir, f"{name}.json")) as f:
            out[name] = json.load(f)
    return out


def sem_ci(arr, alpha=0.05):
    a = np.asarray(arr, float)
    n = len(a)
    mean = a.mean() if n else 0.0
    if n > 1:
        se = stats.sem(a)
        h = se * stats.t.ppf(1 - alpha/2, n-1)
    else:
        h = 0.0
    return mean, h


def update_elo(r_a, r_b, s_a, K=K_ELO):
    e_a = 1/(1 + 10**((r_b - r_a)/400))
    return r_a + K*(s_a - e_a)


def extract_root(m):
    return m.split(':',1)[-1].split('_',1)[0]

            
# -------- normalized-score --------

def compute_normalized(data):
    out = {}
    winrate = {}

    for p, recs in data.items():
        is_two_player = len(recs[0]['model_name']) == 2

        if p in SINGLE_DET:
            seeds = range(1, 11)
        elif p in TWO_DET or p in TWO_DET_IMAGE:
            seeds = range(1, 6)
        elif p in SINGLE_STO:
            seeds = range(1, 101)
        else:
            seeds = range(1, 51)

        scores = {'easy': defaultdict(list), 'normal': defaultdict(list)}
        winrate[p] = {'easy': defaultdict(lambda: defaultdict(int)), 'normal': defaultdict(lambda: defaultdict(int))}

        if not is_two_player:
            for d in ['easy', 'normal']:
                for s in seeds:
                    group = [
                        r for r in recs
                        if (r['difficulty'] == d and r['random_seed'] == s)
                        or (r['difficulty'] == '' and r['random_seed'] is None and random.random() < 0.5)
                    ]
                    if not group:
                        continue

                    if p == "ExclusivityProbesPuzzle":
                        mmin = min(r['score'] for r in group)
                        for r in group:
                            m = r['model_name'][0]
                            scores[d][m].append(mmin / r['score'] if mmin > 0 else 0.0)
                    else:
                        mmax = max(r['score'] for r in group)
                        for r in group:
                            m = r['model_name'][0]
                            scores[d][m].append(r['score'] / mmax if mmax > 0 else 0.0)
        else:
            for r in recs:
                d = r['difficulty'] if r['difficulty'] else ('easy' if random.random() < 0.5 else 'normal')
                m0, m1 = r['model_name']

                # Score attribution
                if r['score'] == 0:
                    s0, s1 = 1.0, 0.0
                    winrate[p][d][m0][m1] += 1
                elif r['score'] == 1:
                    s0, s1 = 0.0, 1.0
                    winrate[p][d][m1][m0] += 1
                else:
                    s0, s1 = 0.5, 0.5
                    # Draw → no change in win count

                scores[d][m0].append(s0)
                scores[d][m1].append(s1)

        out[p] = scores

    # Normalize winrate (convert counts to rates)
    winrate_normalized = {}
    for p in winrate:
        winrate_normalized[p] = {}
        for d in winrate[p]:
            wr = winrate[p][d]
            all_pairs = set((m1, m2) for m1 in wr for m2 in wr[m1])  # all model pairs
            winrate_normalized[p][d] = {
                m1: {
                    m2: wr[m1][m2] / (wr[m1][m2] + wr[m2][m1])
                    if (wr[m1][m2] + wr[m2][m1]) > 0 else 0.0
                    for m2 in wr[m1]
                }
                for m1 in wr
            }
    print("\n=== Winrate Normalized ===")
    for p, dm in winrate_normalized.items():
        print(f"\n{p}:")
        for d in ['easy', 'normal']:
            print(f" [{d}]")
            for m1 in sorted(dm[d]):
                for m2 in sorted(dm[d][m1]):
                    print(f"   {m1} vs {m2} → {dm[d][m1][m2]:.3f}")
    return out


def summarize_normalized(norm, etype):
    # 1) per-puzzle
    print("\n=== Per-Puzzle Normalized Scores ===")
    for p, dm in norm.items():
        print(f"\n{p}:")
        for d in ['easy','normal']:
            print(f" [{d}]")
            for m, vals in sorted(dm[d].items()):
                mean,ci = sem_ci(vals)
                print(f"   {m} → {mean:.3f} ±{ci:.3f}")
            if etype=='code':
                for root in CODE_MODELS:
                    inst = []
                    for m,vals in dm[d].items():
                        if extract_root(m)==root:
                            inst.append(np.mean(vals))
                        elif root == 'custom' and 'custom' in extract_root(m).lower():
                            inst.append(np.mean(vals))
                    if not inst: continue
                    mean,ci = sem_ci(inst)
                    sorted_list = sorted(inst)
                    print(f"     {root} → {mean:.3f} ±{ci:.3f}")
                    print(f"        Sorted: {' '.join(f'{x:.3f}' for x in sorted_list)}")

    # 2) grouped by type
    print("\n=== Grouped Normalized Scores ===")
    if etype=='instruction':
        defs = [SINGLE_DET, TWO_DET, TWO_DET_IMAGE]
        names = ['single-det','two-det','two-det-img']
    else:
        defs = [SINGLE_DET,SINGLE_STO,TWO_DET,TWO_STO]
        names = ['single-det','single-sto','two-det','two-sto']

    for name, grp in zip(names,defs):
        agg={'easy':defaultdict(list),'normal':defaultdict(list)}
        for p in grp:
            for d in ['easy','normal']:
                for m,vals in norm[p][d].items(): agg[d][m].append(np.mean(vals))
        print(f"\n-- {name} --")
        for d in ['easy','normal']:
            print(f" [{d}]")
            for root in CODE_MODELS:
                inst = []
                for m,vals in agg[d].items():
                    if extract_root(m)==root:
                        inst.extend(vals)
                    elif root == 'custom' and 'custom' in extract_root(m).lower():
                        inst.extend(vals)
                if not inst: continue
                mean,ci=sem_ci(inst)
                print(f"     {root} → {mean:.3f} ±{ci:.3f}")
                if etype=='code':
                    sorted_list=sorted(inst)
                    print(f"        Sorted: {' '.join(f'{x:.3f}' for x in sorted_list)}")


    # 3) combined across difficulties
    print("\n=== Combined All Normalized Scores ===")
    combined = SINGLE_DET+TWO_DET if etype=='instruction' else SINGLE_DET+SINGLE_STO+TWO_DET+TWO_STO
    all_vals=defaultdict(list)
    for p in combined:
        for d in ['easy','normal']:
            for m,vals in norm[p][d].items(): all_vals[m].append(np.mean(vals))
    for root in CODE_MODELS:
        inst = []
        for m,vals in all_vals.items():
            if extract_root(m)==root:
                inst.extend(vals)
            elif root == 'custom' and 'custom' in extract_root(m).lower():
                inst.extend(vals)
        if not inst: continue
        mean,ci=sem_ci(inst)
        print(f"     {root} → {mean:.3f} ±{ci:.3f}")
        if etype=='code':
            sorted_list=sorted(inst)
            print(f"        Sorted: {' '.join(f'{x:.3f}' for x in sorted_list)}")

# -------- Elo-score --------

def compute_elo(data):
    out={}
    for p,recs in data.items():
        two=len(recs[0]['model_name'])==2
        elo_map={}
        for d in ['easy','normal']:
            ratings={}
            for r in recs:
                for m in r['model_name']: ratings.setdefault(m,1000.0)
            if two:
                for r in recs:
                    if r['difficulty']!=d:
                        if r['difficulty'] == '': 
                            random_value=random.random()
                            if random_value<0.5: continue
                        else:
                            continue
                    m0,m1=r['model_name']; s0=1 if r['score']==0 else (0 if r['score']==1 else 0.5)
                    r0,r1=ratings[m0],ratings[m1]
                    ratings[m0]=update_elo(r0,r1,s0); ratings[m1]=update_elo(r1,r0,1-s0)
            else:
                seeds=defaultdict(list)
                for r in recs:
                    if r['difficulty']==d: 
                        seeds[r['random_seed']].append(r)
                    elif r['difficulty']=='':
                        random_value=random.random()
                        if random_value<0.5: 
                            if p in SINGLE_DET:
                                random_seed=random.randint(1,10)
                            elif p in SINGLE_STO:
                                random_seed=random.randint(1,100)
                            seeds[random_seed].append(r)
                for grp in seeds.values():
                    # In ExclusivityProbesPuzzle, less score is better
                    if p == "ExclusivityProbesPuzzle":
                        mmin=min(r['score'] for r in grp)
                        norm={r['model_name'][0]:(mmin/r['score'] if mmin>0 else 0.0) for r in grp}
                    else:
                        mmax=max(r['score'] for r in grp)
                        norm={r['model_name'][0]:(r['score']/mmax if mmax>0 else 0.0) for r in grp}
                    items=list(norm.items())
                    for i in range(len(items)):
                        m1,v1=items[i]
                        for j in range(i+1,len(items)):
                            m2,v2=items[j]
                            if extract_root(m1)==extract_root(m2): continue
                            if v1>v2: s1,s2=1,0
                            elif v1<v2: s1,s2=0,1
                            else: s1,s2=0.5,0.5
                            r1,r2=ratings[m1],ratings[m2]
                            ratings[m1]=update_elo(r1,r2,s1); ratings[m2]=update_elo(r2,r1,s2)
            elo_map[d]=ratings
        out[p]=elo_map
    return out


def summarize_elo(elo, etype, data):
    # 1) per-puzzle
    print("\n=== Per-Puzzle Elo Scores ===")
    for p,dm in elo.items():
        print(f"\n{p}:")
        for d in ['easy','normal']:
            print(f" [{d}]")
            for m,r in sorted(dm[d].items()): print(f"   {m} → {r:.1f}")
            if etype=='code':
                for root in CODE_MODELS:
                    inst = []
                    for m,r in dm[d].items():
                        if extract_root(m)==root:
                            inst.append(r)
                        elif root == 'custom' and 'custom' in extract_root(m).lower():
                            inst.append(r)
                    if not inst: continue
                    mean,ci=sem_ci(inst)
                    sorted_list=sorted(inst)
                    print(f"     {root} → {mean:.1f} ±{ci:.1f}")
                    print(f"        Sorted: {' '.join(f'{x:.1f}' for x in sorted_list)}")
    # 2) grouped
    print("\n=== Grouped Elo Scores ===")
    if etype=='instruction':
        defs=[SINGLE_DET,TWO_DET,TWO_DET_IMAGE]; names=['single-det','two-det','two-det-img']
    else:
        defs=[SINGLE_DET,SINGLE_STO,TWO_DET,TWO_STO]; names=['single-det','single-sto','two-det','two-sto']
    for name,grp in zip(names,defs):
        agg={'easy':defaultdict(list),'normal':defaultdict(list)}
        for p in grp:
            for d in ['easy','normal']:
                for m,r in elo[p][d].items(): agg[d][m].append(r)
        print(f"\n-- {name} --")
        for d in ['easy','normal']:
            print(f" [{d}]")
            for root in CODE_MODELS:
                inst = []
                for m,rs in agg[d].items():
                    if extract_root(m)==root:
                        inst.extend(rs)
                    elif root == 'custom' and 'custom' in extract_root(m).lower():
                        inst.extend(rs)
                if not inst: continue
                mean,ci=sem_ci(inst)
                print(f"     {root} → {mean:.1f} ±{ci:.1f}")
                if etype=='code':
                    sorted_list=sorted(inst)
                    print(f"        Sorted: {' '.join(f'{x:.1f}' for x in sorted_list)}")
    # 3) combined
    print("\n=== Combined All Elo Scores ===")
    combined=SINGLE_DET+TWO_DET if etype=='instruction' else SINGLE_DET+SINGLE_STO+TWO_DET+TWO_STO
    allr=defaultdict(list)
    for p in combined:
        for d in ['easy','normal']:
            for m,r in elo[p][d].items(): allr[m].append(r)
    for root in CODE_MODELS:
        inst = []
        for m,rs in allr.items():
            if extract_root(m)==root:
                inst.extend(rs)
            elif root == 'custom' and 'custom' in extract_root(m).lower():
                inst.extend(rs)
        if not inst: continue
        mean,ci=sem_ci(inst)
        print(f"     {root} → {mean:.1f} ±{ci:.1f}")
        if etype=='code':
            sorted_list=sorted(inst)
            print(f"        Sorted: {' '.join(f'{x:.1f}' for x in sorted_list)}")

# -------- main --------

if __name__ == "__main__":
    args = parse_args()
    puzzles = list_puzzles(args.eval_type)
    data = load_all(args.data_dir, puzzles)
    if args.score_type=="normalized score": summarize_normalized(compute_normalized(data), args.eval_type)
    else: summarize_elo(compute_elo(data), args.eval_type, data)