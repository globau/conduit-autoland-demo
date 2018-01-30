#!/usr/bin/env python3

import json
import base64
import subprocess
import sys
import re
import configparser
import email.utils
import os
from urllib import request

# Load .env file.
env = configparser.ConfigParser()
env_file = '{}/.env'.format(os.path.abspath(os.path.dirname(__file__)))
with open(env_file) as f:
    env.read_string('[config]\n{}'.format(f.read()))
env = env['config']

autoland_url = 'http://localhost:{}/autoland'.format(env['HOST_AUTOLAND'])

# Post all commits since last public revision.
commit_log = subprocess.check_output([
    'hg', 'log',
    '-r', 'children(last(public()))::.',
    '-T', '{rev} {node} {author}\n',
]).decode(sys.stdout.encoding)
if not commit_log:
    print('Failed to find any non-public revisions to post')
    sys.exit(1)

# Basic job template.
job = dict(
    destination=env['REPO_NAME'],
    ldap_username=None,
    patch=None,
    pingback_url='http://localhost/',
    rev=None,
    tree=env['REPO_NAME'],
)

commit_log_re = re.compile(
    r'^(?P<rev>\d+)'
    r' (?P<node>[a-z0-9]+)'
    r' (?P<user>.+)\s*$')
for commit_line in commit_log.splitlines():
    m = commit_log_re.match(commit_line)
    if not m:
        continue

    # Fill in job details from commit.
    job['rev'] = m.group('rev')
    job['ldap_username'] = email.utils.parseaddr(m.group('user'))[1]
    job['patch'] = base64.b64encode(
        subprocess.check_output(['hg', 'export', '-r', m.group('node')])
    ).decode('utf-8')

    print('Posting {}'.format(m.group('node')))
    print(job)

    # HTTP Auth
    pass_man = request.HTTPPasswordMgrWithDefaultRealm()
    pass_man.add_password(None, autoland_url, 'autoland', env['AUTOLAND_KEY'])
    auth_handler = request.HTTPBasicAuthHandler(pass_man)
    request.install_opener(request.build_opener(auth_handler))

    # HTTP POST request.
    req = request.Request(
        autoland_url,
        method='POST',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(job, indent=0, sort_keys=True).encode('utf8'))

    # Submit.
    res = request.urlopen(req)
    res_body = res.read()
    response = json.loads(res_body.decode('utf-8'))

    # Show result.
    if 'request_id' not in response:
        print('Submission failed.\n{}'.format(response))
        sys.exit(1)
    print('Submission success: request_id {}'.format(response['request_id']))

