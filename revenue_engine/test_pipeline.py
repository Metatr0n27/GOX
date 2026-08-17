#!/usr/bin/env python3
import os, tempfile
from pathlib import Path
import pipeline
from demand_to_cash import Opportunity

with tempfile.TemporaryDirectory() as td:
    pipeline.STATE_DIR=Path(td); pipeline.QUEUE=Path(td)/"opportunities.json"
    pipeline.scout=lambda:[
        Opportunity("test","1","Hiring automation workflow","Need someone for python automation. Budget $500",500,500,source_url="https://example.test/1"),
        Opportunity("test","2","Logo design","Need a logo",300,300,source_url="https://example.test/2"),
    ]
    payload=pipeline.build_queue()
    assert payload["count"]==1
    item=payload["items"][0]
    assert item["state"]=="PROPOSAL_READY"
    assert item["budget_max"]==500
    assert item["proposal"]["requires_owner_submission"] is True
    reread=pipeline.read_queue()
    assert reread["items"][0]["id"]==item["id"]
print("PASS: scout -> qualification -> ranked proposal-ready persistence")
