#!/usr/bin/env python3
"""Fail-closed repository secret scanner for obvious credential leaks."""
import os,re,sys
from pathlib import Path

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.')
SKIP={'.git','node_modules','.venv','venv','__pycache__'}
TEXT_EXT={'.py','.sh','.md','.json','.yaml','.yml','.toml','.ini','.env','.txt','.html','.js','.ts','.tsx','.jsx'}
PATTERNS=[
 ('private_key',re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |)?PRIVATE KEY-----')),
 ('github_token',re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}\b')),
 ('generic_bearer',re.compile(r'(?i)\bauthorization\s*[:=]\s*bearer\s+[A-Za-z0-9._~+/=-]{16,}')),
 ('api_secret_assignment',re.compile(r'(?i)\b(?:api[_-]?key|secret|password|access[_-]?token)\b\s*[:=]\s*["\'](?!CHANGE_ME|REDACTED|example|placeholder)[^"\']{12,}["\']')),
]
ALLOW_MARKERS=('example','placeholder','redacted','test-only','dummy')

def scan():
    findings=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in SKIP for x in p.parts): continue
        if p.suffix.lower() not in TEXT_EXT and p.name not in {'.env','.gitignore'}: continue
        try: text=p.read_text(errors='ignore')
        except Exception: continue
        for i,line in enumerate(text.splitlines(),1):
            low=line.lower()
            if any(m in low for m in ALLOW_MARKERS): continue
            for name,rx in PATTERNS:
                if rx.search(line): findings.append((str(p),i,name))
    return findings

if __name__=='__main__':
    f=scan()
    if f:
        for p,i,n in f: print(f'FAIL {n} {p}:{i}')
        sys.exit(1)
    print('SECRET_GUARD=PASS')
