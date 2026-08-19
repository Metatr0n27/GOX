#!/usr/bin/env python3
"""Generate controlled behavioral variants from GOX family profiles.

For each real consented profile, produce percentage-shifted archetypes and then
10 small variants of every archetype. Synthetic profiles are always labelled so
GOX never confuses them with the real family member.
"""
from __future__ import annotations
import argparse, copy, json, random
from pathlib import Path

NUMERIC = ("decision_speed","risk_tolerance","structure_need","directness","social_energy","change_tolerance")
DEFAULT_PCTS = (-30,-20,-10,0,10,20,30)

def clamp(v): return max(1, min(5, int(round(v))))

def shifted(base, pct):
    out=copy.deepcopy(base)
    out["synthetic"]=True
    out["derived_from"]=base.get("profile_id")
    out["variation_percent"]=pct
    out["profile_id"]=f'{base["profile_id"]}-shift-{pct:+d}'
    out["display_name"]=f'{base["display_name"]} synthetic {pct:+d}%'
    b=out.get("behavior",{})
    # Alternate direction by trait so a percentage creates a genuinely different
    # behavioral mix rather than making every trait simply larger/smaller.
    direction={"decision_speed":1,"risk_tolerance":1,"structure_need":-1,
               "directness":1,"social_energy":1,"change_tolerance":1}
    for k in NUMERIC:
        if k in b:
            b[k]=clamp(b[k]*(1 + direction[k]*pct/100.0))
    return out

def child_variant(parent, n, rng):
    out=copy.deepcopy(parent)
    out["variant_number"]=n
    out["profile_id"]=f'{parent["profile_id"]}-v{n:02d}'
    out["display_name"]=f'{parent["display_name"]} / variant {n:02d}'
    b=out.get("behavior",{})
    # Small deterministic perturbations: usually one or two traits move one step.
    keys=rng.sample([k for k in NUMERIC if k in b], k=min(rng.choice((1,1,2)), len(NUMERIC)))
    for k in keys:
        b[k]=clamp(b[k] + rng.choice((-1,1)))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("profile", type=Path)
    ap.add_argument("--out", type=Path, default=Path("family_variants"))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--percent", type=int, nargs="*", default=list(DEFAULT_PCTS))
    args=ap.parse_args()
    base=json.loads(args.profile.read_text(encoding="utf-8"))
    if not base.get("consent",{}).get("agreed"):
        raise SystemExit("Profile does not contain consent; refusing to derive variants.")
    root=args.out/base["profile_id"]
    root.mkdir(parents=True, exist_ok=True)
    manifest=[]
    for pct in args.percent:
        parent=shifted(base,pct)
        group=root/f"shift_{pct:+d}"
        group.mkdir(exist_ok=True)
        (group/"base.json").write_text(json.dumps(parent,indent=2),encoding="utf-8")
        rng=random.Random(f"{args.seed}:{base['profile_id']}:{pct}")
        children=[]
        for n in range(1,11):
            child=child_variant(parent,n,rng)
            p=group/f"variant_{n:02d}.json"
            p.write_text(json.dumps(child,indent=2),encoding="utf-8")
            children.append(str(p))
        manifest.append({"percent":pct,"base":str(group/"base.json"),"variants":children})
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(f"Generated {len(args.percent)} percentage profiles and {len(args.percent)*10} child variants in {root}")

if __name__=="__main__": main()
