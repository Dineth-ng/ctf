#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[1]
config = dict(line.split('=', 1) for line in (root / '.env').read_text().splitlines() if line and not line.startswith('#'))
env = os.environ.copy()
keys = ['NH_ADMIN_NAME', 'NH_ADMIN_EMAIL', 'NH_ADMIN_PASSWORD']
env.update({key: config[key] for key in keys})
cmd = ['docker', 'compose', 'exec', '-T']
for key in keys:
    cmd.extend(['--env', key])
cmd.extend(['ctfd', 'python', '-'])
subprocess.run(cmd, input=(root / 'scripts/bootstrap_ctfd.py').read_text(), text=True, cwd=root, env=env, check=True)
out = root / '.local/admin-credentials.txt'
out.parent.mkdir(exist_ok=True)
fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(f"Admin URL: http://localhost:8000/admin\nUsername: {config['NH_ADMIN_NAME']}\nEmail: {config['NH_ADMIN_EMAIL']}\nPassword: {config['NH_ADMIN_PASSWORD']}\n")
print('Admin credentials saved privately in .local/admin-credentials.txt')
