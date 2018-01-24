#!/usr/bin/env python3

import configparser
import os
import subprocess
import sys

# Read config from .env
parser = configparser.ConfigParser()
env_file = '{}/.env'.format(os.path.abspath(os.path.dirname(__file__)))
with open(env_file) as f:
    parser.read_string('[config]\n{}'.format(f.read()))
env = parser['config']

# Determine output path
if len(sys.argv) == 1:
    output_path = env['REPO_NAME']
else:
    output_path = sys.argv[1]
if os.path.exists(output_path):
    print('{} already exists'.format(output_path))
    sys.exit(1)

# Clone
print('cloning into {}'.format(output_path))
subprocess.call([
    'hg',
    'clone', 'http://localhost:{}'.format(env['HOST_HGWEB']),
    output_path
])

# Set pushurl so you can't push directly to the repo (must use autoland).
hgrc_file = '{}/.hg/hgrc'.format(output_path)
hgrc = configparser.ConfigParser()
with open(hgrc_file) as f:
    hgrc.read_file(f)
hgrc['paths']['default:pushurl'] = 'file:///dev/null'
with open(hgrc_file, 'w') as f:
    hgrc.write(f)
