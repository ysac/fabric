# -*- encoding:utf-8 -*-
#
# base setup
#

from fabric.api import *
from cuisine import *


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
PUBKEYS_DIR = WORK_DIR + '/pubkeys'
SHADOWS_DIR = WORK_DIR + '/shadows'

USERS = [
  'hoge',
  'fuga'
]

RPMS = [
  'jq',
  'sysstat',
  'strace',
  'telnet',
  'tree',
  'unzip',
  'wget',
  'zip'
]

select_package('yum')


@task
def base_setup():
  add_yum_repositories()
  package_upgrade()
  update_rpms(RPMS)
  setup_sudo()
  update_users(USERS)


@task
def users_update():
  update_users(USERS)


@task
def rpms_update():
  update_rpms(RPMS)


def update_users(users):
  for user in users:
    # ユーザ追加
    shadow_file = SHADOWS_DIR + '/cryptpw.' + user
    if os.path.isfile(shadow_file):
      is_crypt = True
      init_passwd = file_local_read(shadow_file).rstrip()
    else:
      is_crypt = False
      init_passwd = user + '00'

    user_ensure(
      user,
      passwd = init_passwd,
      encrypted_passwd = is_crypt
    )

    # SSH設定
    pubkey_file = PUBKEYS_DIR + '/id_rsa.' + user + '.pub'
    with mode_sudo():
      ssh_authorize(
        user,
        file_local_read(pubkey_file)
      )

    # グループ設定
    group_user_ensure('wheel', user)


def update_rpms(rpms):
  for rpm in rpms:
    with mode_sudo():
      package_ensure(rpm, update=False)


def setup_sudo():
  file_write(
    location = '/etc/sudoers.d/wheel',
    content  = '%wheel ALL=(ALL) ALL\n',
    mode = '600',
    owner = 'root',
    group = 'root',
    sudo = True
  )  


def add_yum_repositories():
  add_epel()
  add_remi()
  add_rpmforge()


def add_epel():
  sudo('rpm --import http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-6')
  sudo('rpm -iv http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm', warn_only=True)


def add_remi():
  sudo('rpm --import http://rpms.famillecollet.com/RPM-GPG-KEY-remi')
  sudo('rpm -iv http://rpms.famillecollet.com/enterprise/remi-release-6.rpm', warn_only=True)


def add_rpmforge():
  sudo('rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt')
  sudo('rpm -iv http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm', warn_only=True)

