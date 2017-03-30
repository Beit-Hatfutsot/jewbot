from __future__ import with_statement
from datetime import datetime
from fabric.api import *
from fabric.contrib import files

env.user = 'bhs'
env.use_ssh_config = True
env.now = datetime.now().strftime('%Y%m%d-%H%M')

def push_code(rev='HEAD', virtualenv=True, requirements=True, cur_date=None):
    if cur_date is None:
        cur_date = run("date +%d.%m.%y-%H:%M:%S")
    local('git archive -o /tmp/jewbot.tar.gz '+rev)
    put('/tmp/jewbot.tar.gz', '/tmp')
    run('mv jewbot /tmp/latest-jewbot-{}'.format(cur_date))
    run('mkdir jewbot')
    with cd("jewbot"):
        run('tar xzf /tmp/jewbot.tar.gz')
        if virtualenv:
            if not files.exists('env'):
                run('virtualenv -p /usr/bin/python3 env')
        if requirements:
            with prefix('. env/bin/activate'):
                run('pip install -r requirements.txt')
    run('rm -rf /tmp/jewbot-*')
    run('mv /tmp/latest-jewbot-{} /tmp/jewbot-{}'.format(cur_date, cur_date))
    run('cp /tmp/jewbot-{}/local_config.py jewbot/local_config.py'.format(cur_date))

@hosts("bhs-dev")
def deploy():
    push_code()
