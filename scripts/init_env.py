#!/usr/bin/env python3
"""Generate per-deployment secrets; never overwrite an existing configuration."""
import os
import secrets
from pathlib import Path
root = Path(__file__).resolve().parents[1]
path = root / '.env'
if not path.exists():
    fields = {key: secrets.token_hex(24) for key in (
        'CTFD_SECRET_KEY', 'CTFD_DB_PASSWORD', 'CTFD_DB_ROOT_PASSWORD', 'STAGE4_DB_ROOT_PASSWORD')}
    fields.update(NH_ADMIN_NAME='nighthawk_admin', NH_ADMIN_EMAIL='admin@nighthawk.local',
                  NH_ADMIN_PASSWORD=secrets.token_urlsafe(24))
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(''.join(f'{k}={v}\n' for k, v in fields.items()))
    print('Created .env with unique secrets (permissions 600).')
else:
    print('Using existing .env; secrets preserved.')
