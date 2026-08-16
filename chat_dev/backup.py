#!/usr/bin/env python3
"""Online-safe SQLite backup for GOX Chat Dev."""
import datetime
import os
import sqlite3

DATA_DIR=os.getenv('GOX_DATA_DIR',os.path.join(os.path.dirname(__file__),'data'))
DB_PATH=os.path.join(DATA_DIR,'chat_dev.sqlite3')
BACKUP_DIR=os.getenv('GOX_BACKUP_DIR',os.path.join(DATA_DIR,'backups'))
os.makedirs(BACKUP_DIR,exist_ok=True)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
dest=os.path.join(BACKUP_DIR,f'chat_dev-{stamp}.sqlite3')
with sqlite3.connect(DB_PATH) as src, sqlite3.connect(dest) as dst:
    src.backup(dst)
    row=dst.execute('PRAGMA integrity_check').fetchone()
    if not row or row[0] != 'ok': raise RuntimeError(f'backup integrity check failed: {row}')
print(dest)
