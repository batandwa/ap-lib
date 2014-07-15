#!/usr/bin/python

# Run with:
#   python hello.py cameron
#   python hello.py


# import modules used here -- sys is a very standard one
import argparse
import os
import subprocess
import sys

playbooks_path = os.path.realpath(os.path.expanduser(os.getenv('APLIB_PLAYBOOK_PATH', '~/.ansible/playbooks')))
roles_path = os.path.realpath(os.path.expanduser(os.getenv('APLIB_ROLES_PATH', '~/.ansible/roles')))
args = None
extra_args = None

def setup_arguments():
  global args
  global extra_args
  global extra_args

  parser = argparse.ArgumentParser(description='An application that calls ansible-playbook and allows for a centralised playbook location.')
  
  parser.add_argument('operation', help='The operation to be executed')
  parser.add_argument('playbook', default='', help='The playbook to be executed.', nargs='?')

  args, extra_args = parser.parse_known_args()
  
def check_conf():
  # Check that the Playbook storage is set
  if(not os.path.isdir(playbooks_path)):
    return False

  return True

def errors(err):
  return {
    'NO_PLAYBOOK_DIR': {'code': 1, 'title': 'Playbook directory does not exist.'},
    'NO_SETUP': {'code': 2, 'title': 'Playbook directory does not exist.'},
    'NO_HOSTS_PATH_DECLARATION': {'code': 4, 'title': 'There was an error in the hosts file declaration.'}
  }[err]

def check_hosts_file():
  global extra_args

  hosts_path_arg = '-i'
  cur_path = os.getcwd()

  if hosts_path_arg in extra_args:
    arg_hosts_path_id = extra_args.index(hosts_path_arg) + 1
    if extra_args[arg_hosts_path_id] == None:
      sys.exist(errors('NO_HOSTS_PATH_DECLARATION'))
    # return extra_args[arg_hosts_path_id]
  elif os.path.isfile(cur_path + '/hosts'):
    extra_args += ['-i', cur_path + '/hosts']
    print extra_args
    return cur_path + '/hosts'
  else:
    return None


def main():
  setup_arguments()

  global args
  global extra_args

  check_hosts_file()

  if(not check_conf()):
    print 'Error with environment setup.'
    sys.exit(errors('NO_SETUP')['code'])

  if(args.operation == 'discover'):
    for root, dirs, files in os.walk(playbooks_path):
      for file in files:
        if file.endswith(".yml"):
          print os.path.join(root, file).replace(playbooks_path, '').lstrip('/')
    sys.exit(0)

  if(args.operation == 'run'):
    ansible_cmd = ['ansible-playbook', playbooks_path + '/' + args.playbook] + extra_args
    print ansible_cmd

    subprocess.call(ansible_cmd)

if __name__ == '__main__':
  main()
