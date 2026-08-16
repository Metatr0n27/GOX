#!/usr/bin/env python3
import sqlite3
from revenue import init_revenue_schema, upsert_opportunity, score, record_revenue, collected_since

c=sqlite3.connect(':memory:')
init_revenue_schema(c)
item={"source":"test","source_ref":"job-1","title":"Clean spreadsheet","deliverable":"clean xlsx","gross_payout":250,"estimated_cost":10,"win_probability":.5,"same_day_probability":.8,"fulfillment_minutes":60,"capability":"spreadsheet"}
a=upsert_opportunity(c,item)
b=upsert_opportunity(c,{**item,"title":"Updated title"})
assert a==b
assert c.execute('select count(*) from opportunities').fetchone()[0]==1
s=score(250,10,.5,.8,60)
assert s['net_payout']==240
assert s['expected_value_today']==96
try:
    record_revenue(c,a,250,None)
    raise AssertionError('unverified revenue accepted')
except ValueError: pass
record_revenue(c,a,250,{"type":"payment_receipt","ref":"test-only"})
assert collected_since(c,0)==250
print('PASS: dedupe -> score -> evidence gate -> collected revenue')
