#!/usr/bin/env python3
"""Exercise live services and real CTFd submissions. Creates then deletes one test player."""
import io, json, os, re, secrets, subprocess, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://localhost:8000'
STAGES = json.loads((ROOT/'ctfd/challenges.json').read_text())
results = []
admin, player, test_id = requests.Session(), requests.Session(), None

def check(condition, label):
    results.append({'check': label, 'passed': bool(condition)})
    print(('PASS ' if condition else 'FAIL ') + label, flush=True)
    if not condition:
        raise AssertionError(label)

def nonce(session, route):
    r = session.get(BASE+route, timeout=15)
    r.raise_for_status()
    m = re.search(r'name="nonce"[^>]*value="([^"]+)"', r.text)
    if not m:
        m = re.search(r"'csrfNonce':\s*\"([^\"]+)\"", r.text)
    if not m:
        raise RuntimeError('Missing CSRF token')
    return m.group(1)

def api(session, method, route, data=None):
    token = nonce(session, '/challenges')
    return session.request(method, BASE+'/api/v1'+route, json=data,
                           headers={'CSRF-Token':token,'Content-Type':'application/json'}, timeout=20)

def command(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True, timeout=45, **kwargs).stdout

try:
    cfg=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if line and not line.startswith('#'))
    token=nonce(admin,'/login')
    admin.post(BASE+'/login',data={'name':cfg['NH_ADMIN_NAME'],'password':cfg['NH_ADMIN_PASSWORD'],'nonce':token},timeout=15)
    r=admin.get(BASE+'/admin',timeout=15)
    check(r.status_code==200 and '/login' not in r.url, 'Admin login')
    catalog=api(admin,'GET','/challenges?view=admin').json()['data']
    by_name={c['name']:c['id'] for c in catalog}
    ids=[by_name[f'{n}. {s[0]}'] for n,s in enumerate(STAGES,1)]
    check(len(ids)==6,'All six configured challenges')
    who='validation_'+secrets.token_hex(5)
    token=nonce(player,'/register')
    r=player.post(BASE+'/register',data={'name':who,'email':who+'@nighthawk.local',
                   'password':secrets.token_urlsafe(24),'nonce':token},timeout=15)
    users=api(admin,'GET','/users').json()['data']
    test_id=next(u['id'] for u in users if u['name']==who)
    check('/register' not in r.url,'Player registration')
    check(api(player,'POST','/challenges/attempt',{'challenge_id':ids[1],'submission':STAGES[1][3]}).status_code==403,
          'Stage 2 rejects submissions before Stage 1 is solved')
    check(requests.get('http://localhost:8080/dashboard.php',timeout=15).url.endswith('index.php'),
          'Stage 4 dashboard requires a session')
    # Recover flags from actual served/downloaded evidence, not source-code grep.
    jpg=requests.get('http://localhost/employee.jpg',timeout=15); jpg.raise_for_status()
    flag1=Image.open(io.BytesIO(jpg.content)).getexif().get(0x9286)
    image=Image.open(io.BytesIO(requests.get('http://localhost/trophy.png',timeout=15).content)).convert('RGB')
    bits=[v&1 for pixel in image.getdata() for v in pixel]
    raw=bytes(sum(bits[i+j]<<(7-j) for j in range(8)) for i in range(0,len(bits)-7,8))
    msg=raw[4:4+int.from_bytes(raw[:4],'big')].decode()
    flag2=re.search(r'NH\{[^}]+\}',msg).group()
    flag3=re.search(r'NH\{[^}]+\}',command(['python3','stage3_crypto/solve_stage3.py'])).group()
    portal=requests.Session()
    r=portal.post('http://localhost:8080/',data={'username':"' OR 1=1#",'password':'invalid'},timeout=15)
    flag4=re.search(r'NH\{[^}]+\}',r.text).group()
    flag5=re.search(r'COMBINED STAGE 5 FLAG: (NH\{[^}]+\})',command(['python3','stage5_forensics/solve_stage5.py'])).group(1)
    env=os.environ.copy(); env.update(SSH_ASKPASS=str(ROOT/'scripts/ssh_askpass.sh'),
        SSH_ASKPASS_REQUIRE='force',DISPLAY=':0',NH_SSH_PASSWORD='nighthawk_guest')
    ssh=['ssh','-p','2222','-o','StrictHostKeyChecking=accept-new','-o',f'UserKnownHostsFile={ROOT}/.local/known_hosts',
         '-o','PreferredAuthentications=password','-o','NumberOfPasswordPrompts=1','runner@localhost']
    output=command(ssh+['id -u; test ! -r /opt/vault/vault.enc && echo VAULT_PROTECTED; sudo -l'],
                   env=env,stdin=subprocess.DEVNULL,start_new_session=True)
    check('VAULT_PROTECTED' in output and output.splitlines()[0]!='0','SSH starts as a low privilege user; vault is protected')
    output=command(ssh+['sudo find /home/runner -maxdepth 0 -exec /opt/vault/vault_lock /opt/vault/vault.enc \\;'],
                   env=env,stdin=subprocess.DEVNULL,start_new_session=True)
    flag6=re.search(r'NH\{[^}]+\}',output).group()
    for n,(cid,flag,stage) in enumerate(zip(ids,[flag1,flag2,flag3,flag4,flag5,flag6],STAGES),1):
        check(flag==stage[3],f'Stage {n}: recovered flag equals canonical flag')
        detail=api(player,'GET',f'/challenges/{cid}').json()['data']
        check(stage[3] not in detail['description'],f'Stage {n}: description does not reveal answer')
        for file in detail['files']:
            response=player.get(BASE+file,timeout=20)
            check(response.status_code==200,f'Stage {n}: evidence download works')
            if file.split('?')[0].endswith('trophy.png'):
                check(response.content==requests.get('http://localhost/trophy.png',timeout=15).content,'CTFd and web stego images match')
            else:
                filename=file.split('?')[0].rsplit('/',1)[-1]
                path=ROOT/('stage3_crypto' if filename=='chat_log.txt' else 'stage5_forensics')/filename
                check(response.content==path.read_bytes(),f'Stage {n}: uploaded evidence matches source')
        wrong=api(player,'POST','/challenges/attempt',{'challenge_id':cid,'submission':'NH{incorrect_test}'})
        check(wrong.json()['data']['status']=='incorrect',f'Stage {n}: wrong flag rejected')
        correct=api(player,'POST','/challenges/attempt',{'challenge_id':cid,'submission':flag})
        check(correct.json()['data']['status']=='correct',f'Stage {n}: correct flag accepted')
    me=api(player,'GET','/users/me').json()['data']
    check(me['score']==sum(s[2] for s in STAGES),'Player score totals 1300 points')
    duplicate=api(player,'POST','/challenges/attempt',{'challenge_id':ids[0],'submission':flag1})
    check(duplicate.json()['data']['status']=='already_solved','Duplicate solve does not award more points')
    # Verify network metadata and a real blocked cross-network connection.
    containers=json.loads(command(['docker','inspect']+command(['docker','compose','ps','-q']).split()))
    services={c['Config']['Labels']['com.docker.compose.service']:c for c in containers}
    check(all(c['State'].get('Health',{}).get('Status')=='healthy' for c in containers),'All eight services healthy')
    check(all(not c['HostConfig']['Privileged'] for c in containers),'No privileged containers')
    check(services['ctfd']['Config']['User']=='1001:1001','CTFd runs as non-root')
    for name,c in services.items():
        if name=='gateway':
            check(all(b['HostIp']=='127.0.0.1' for bindings in c['HostConfig']['PortBindings'].values() for b in bindings),'Gateway ports are bound to localhost')
        else:
            check(not c['HostConfig']['PortBindings'],f'{name}: no direct published ports')
        check(not any(m['Destination']=='/var/run/docker.sock' for m in c['Mounts']),f'{name}: no Docker socket mount')
    for name in ('platform','platform_front','web_front','web_challenge','osint','vault'):
        network=json.loads(command(['docker','network','inspect','nighthawk-member1_'+name]))[0]
        check(network['Internal'],f'{name}: internal Docker network')
    target=next(iter(services['ctfd_db']['NetworkSettings']['Networks'].values()))['IPAddress']
    probe='import socket; s=socket.socket(); s.settimeout(2)\ntry:\n s.connect(("'+target+'",3306)); print("CONNECTED")\nexcept OSError:\n print("BLOCKED")'
    output=command(['docker','compose','exec','-T','stage6_vault','python3','-c',probe])
    check('BLOCKED' in output,'Vault cannot connect directly to CTFd database')
except Exception as exc:
    print('VALIDATION FAILED:',str(exc),file=sys.stderr)
    results.append({'check':'Run completed','passed':False,'error':str(exc)})
finally:
    if test_id is not None:
        try:
            r=api(admin,'DELETE',f'/users/{test_id}')
            check(r.status_code==200 and r.json()['success'],'Temporary validation account removed')
        except Exception as exc:
            results.append({'check':'Temporary account removal','passed':False,'error':str(exc)})
    report={'time':datetime.now(ZoneInfo('Asia/Colombo')).isoformat(),'checks':results,
            'passed':all(x['passed'] for x in results)}
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/validation.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(0 if report['passed'] else 1)
