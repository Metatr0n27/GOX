#!/usr/bin/env python3
import time
import adapters

assert adapters.execute('plan', {'message':'hello'})['accepted'] is True
try:
    adapters.execute('missing', {'message':'hello'})
    raise AssertionError('unknown capability accepted')
except adapters.UnknownCapability:
    pass
try:
    adapters.execute('plan', {'message':''})
    raise AssertionError('empty message accepted')
except adapters.ValidationError:
    pass

def slow(payload):
    time.sleep(.5)
    return {'ok':True}

adapters.REGISTRY['slow-test']={
    'handler':slow,
    'permission_class':'test',
    'timeout_seconds':.05,
    'side_effecting':False,
    'description':'test only',
}
try:
    adapters.execute('slow-test', {})
    raise AssertionError('timeout not enforced')
except adapters.AdapterTimeout:
    pass
print('PASS: adapter validation -> unknown block -> enforced timeout')
