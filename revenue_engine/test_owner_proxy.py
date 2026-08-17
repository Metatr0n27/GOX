#!/usr/bin/env python3
from owner_proxy import verify_opportunity, verify_delivery

ready={"state":"PROPOSAL_READY","source_url":"https://example.test/job","budget_max":750,"capability":"automation workflow","score":500,"proposal":{"message":"Prepared proposal"}}
r=verify_opportunity(ready,{"ready":True,"blockers":[]})
assert r["verdict"]=="READY_FOR_OWNER_SUBMIT"
assert r["human_required"]==["submit_from_personal_marketplace_account"]
blocked=verify_opportunity({"state":"DISCOVERED","budget_max":0},{"ready":False,"blockers":["capability not verified"]})
assert blocked["verdict"]=="KEEP_WORKING"
d=verify_delivery({"acceptance_criteria":["works"],"test_evidence":["test log"],"tests_passed":True,"known_failures":[]})
assert d["verdict"]=="READY_TO_DELIVER"
assert verify_delivery({})["verdict"]=="KEEP_WORKING"
print("PASS: owner-proxy opportunity and delivery gates")
