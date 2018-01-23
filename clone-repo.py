#!/usr/bin/env python3

import configparser
import os
import subprocess
import sys

env = configparser.ConfigParser()
env_file = '{}/.env'.format(os.path.abspath(os.path.dirname(__file__)))
with open(env_file) as f:
    env.read_string('[config]\n{}'.format(f.read()))
env = env['config']

if len(sys.argv) == 1:
    output_path = env['REPO_NAME']
else:
    output_path = sys.argv[1]
print('cloning into {}'.format(output_path))

subprocess.call([
    'hg',
    'clone', 'http://localhost:{}'.format(env['HOST_HGWEB']),
    output_path
])
