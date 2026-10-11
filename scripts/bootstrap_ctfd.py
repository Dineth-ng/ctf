"""Run inside the pinned CTFd image, using its models and upload utility."""
import os
from pathlib import Path
from werkzeug.datastructures import FileStorage
from CTFd import create_app
from CTFd.models import db, Admins, Users, Challenges, Flags, Hints, Pages, ChallengeFiles
from CTFd.utils import set_config
from CTFd.cache import cache
from CTFd.utils.uploads import upload_file

STAGES = __import__("json").loads(Path("/srv/config/challenges.json").read_text())
app = create_app()
with app.app_context():
    name = os.environ['NH_ADMIN_NAME']
    admin = Users.query.filter_by(name=name).first()
    if admin is None:
        admin = Admins(name=name, email=os.environ['NH_ADMIN_EMAIL'],
                       password=os.environ['NH_ADMIN_PASSWORD'], type='admin', hidden=True, verified=True)
        db.session.add(admin)
    elif admin.type != 'admin':
        raise RuntimeError('Configured admin name belongs to a non-admin account')
    # Existing admin passwords are deliberately preserved on repeat deployment.
    configs = dict(ctf_name='Operation NightHawk: The GhostByte Files',
                   ctf_description='Investigate the NexaCore incident across six stages.',
                   user_mode='users', challenge_visibility='private', account_visibility='public',
                   score_visibility='public', registration_visibility='public', verify_emails=False,
                   ctf_theme='core-beta', setup=True, social_shares=False, challenge_ratings='disabled')
    for key, value in configs.items():
        set_config(key, value)
    page = Pages.query.filter_by(route='index').first()
    if page is None:
        page = Pages(title='Operation NightHawk', route='index', draft=False)
        db.session.add(page)
    page.content = '''<div class="container py-5"><p class="text-uppercase">NexaCore Dynamics · Incident Response</p>
<h1>Operation NightHawk</h1><h3>The GhostByte Files</h3>
<p>Project Prometheus has been compromised. Follow the digital trail through six progressively unlocked investigations.</p>
<p>OSINT → Steganography → Cryptography → Web Security → Forensics → The Vault</p>
<p>Create a player account, open Challenges, and submit flags in the format <code>NH{...}</code>.</p>
<p>Stages 1–2: Easy · Stages 3–4: Moderate · Stage 5: Moderate–Hard · Stage 6: Hard</p>
<p>Practice only against the provided local services. Download evidence from each challenge; hints are free.</p>
<a class="btn btn-primary" href="/challenges">Begin the investigation</a></div>'''
    db.session.commit()
    previous = None
    for number, (title, category, value, flag, description, connection, hint, files) in enumerate(STAGES, 1):
        title = f'{number}. {title}'
        challenge = Challenges.query.filter_by(name=title).first()
        if challenge is None:
            challenge = Challenges(name=title, type='standard')
            db.session.add(challenge)
            db.session.flush()
        challenge.category, challenge.value = category, value
        challenge.description, challenge.connection_info = description, connection
        challenge.state, challenge.position = 'visible', number
        challenge.requirements = {'prerequisites': [previous.id], 'anonymize': True} if previous else None
        if previous:
            previous.next_id = challenge.id
        existing = Flags.query.filter_by(challenge_id=challenge.id).all()
        if len(existing) != 1 or existing[0].content != flag:
            for item in existing:
                db.session.delete(item)
            db.session.add(Flags(challenge_id=challenge.id, type='static', content=flag, data=''))
        item = Hints.query.filter_by(challenge_id=challenge.id).first()
        if item is None:
            item = Hints(challenge_id=challenge.id, cost=0)
            db.session.add(item)
        item.content = hint
        db.session.commit()
        for filename in files:
            location = f'nighthawk-stage-{number}/{filename}'
            with (Path('/srv/artifacts') / filename).open('rb') as fp:
                upload_file(file=FileStorage(stream=fp, filename=filename), type='challenge',
                                challenge_id=challenge.id, location=location)
        previous = challenge
    db.session.commit()
    cache.clear()
    print('CTFd configured: admin, six challenges, exact flags, hints, prerequisites, and four evidence files.')
