#!/usr/bin/env python3
from easy_prompts import CATALOG, list_prompts, resolve

required = {"check-gox", "fix-chatdev", "deploy-chatdev", "test-everything", "show-status", "find-money", "run-500-engine"}
assert required <= set(CATALOG)
assert len(list_prompts()) == len(CATALOG)
assert resolve("check-gox")["requires_approval"] is False
assert resolve("deploy-chatdev")["requires_approval"] is True
assert resolve("does-not-exist") is None
for key, item in CATALOG.items():
    assert item["name"] and item["workflow"] and item["permission"]
print("PASS: Easy Prompts catalog -> workflows -> approval metadata")
