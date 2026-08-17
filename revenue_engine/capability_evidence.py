#!/usr/bin/env python3
"""Runtime evidence registry for GOX sellable capabilities."""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT=Path(os.environ.get("GOX_CAPABILITY_EVIDENCE","/var/lib/gox/capabilities"))
MAX_EVIDENCE_AGE_DAYS=int(os.environ.get("GOX_CAPABILITY_EVIDENCE_MAX_DAYS","30"))


def path_for(slug:str)->Path:
    return ROOT/f"{slug}.json"


def read(slug:str)->dict|None:
    try: data=json.loads(path_for(slug).read_text())
    except (FileNotFoundError,json.JSONDecodeError,OSError): return None
    verified_at=float(data.get("verified_at",0) or 0)
    fresh=(time.time()-verified_at) <= MAX_EVIDENCE_AGE_DAYS*86400 if verified_at else False
    data["fresh"]=fresh
    data["verified"]=bool(data.get("passed")) and fresh
    return data


def write(slug:str,payload:dict)->dict:
    ROOT.mkdir(parents=True,exist_ok=True)
    payload={**payload,"verified_at":time.time()}
    tmp=path_for(slug).with_suffix('.tmp')
    tmp.write_text(json.dumps(payload,indent=2,sort_keys=True))
    os.replace(tmp,path_for(slug))
    return payload
