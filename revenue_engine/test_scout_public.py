#!/usr/bin/env python3
from scout_public import explicit_demand, extract_budget, parse_atom

assert explicit_demand("[Hiring] Automation specialist", "Need someone to build n8n workflows")
assert not explicit_demand("[For Hire] Automation specialist", "Available for work")
assert extract_budget("Budget $500-$1500") == (500.0, 1500.0)
assert extract_budget("Pay $30-$50/hour") == (120.0, 200.0)

xml = b'''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><id>x1</id><title>[Hiring] AI automation</title><content>Need help with OpenAI and n8n. Budget $500-$900.</content><link href="https://example.com/x1"/></entry>
<entry><id>x2</id><title>[For Hire] AI automation</title><content>I am available for work.</content><link href="https://example.com/x2"/></entry>
</feed>'''
items = parse_atom(xml, "test")
assert len(items) == 1
assert items[0].external_id == "x1"
assert items[0].budget_min == 500.0 and items[0].budget_max == 900.0
print("PASS: public scout explicit-demand and budget filters")
