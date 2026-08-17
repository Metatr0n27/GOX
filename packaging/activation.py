#!/usr/bin/env python3
"""Truthful activation gate for packaged GOX editions."""
from __future__ import annotations
import json,sys,time
from pathlib import Path

def check(config):
 p=config.get("profile",{});cap=p.get("proven_capabilities") or p.get("capabilities") or "";channels=p.get("sales_channels") or p.get("contact_channels") or ""
 checks={"edition_selected":bool(config.get("edition")),"goal_defined":bool(str(p.get("goal","")).strip()),"verified_capabilities_supplied":bool(str(cap).strip()),"contact_path_configured":bool(str(channels).strip()),"scoreboard_present":isinstance(config.get("scoreboard"),dict),"real_opportunity_test_passed":bool(config.get("activation",{}).get("real_opportunity_test_passed"))}
 ready=all(checks.values());return {"ready":ready,"state":"ACTIVATED" if ready else "BLOCKED","checks":checks,"next_gap":next((k for k,v in checks.items() if not v),None),"checked_at":time.time()}
def main(argv):
 if len(argv)!=2:raise SystemExit("usage: activation.py CUSTOMER_CONFIG.json")
 path=Path(argv[1]);cfg=json.loads(path.read_text());result=check(cfg);cfg["activation"]={**cfg.get("activation",{}),**result};path.write_text(json.dumps(cfg,indent=2,sort_keys=True));print(json.dumps(result,indent=2))
if __name__=="__main__":main(sys.argv)
