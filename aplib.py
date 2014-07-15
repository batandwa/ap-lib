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

  # create the top-level parser
  parser = argparse.ArgumentParser(description='An application that calls ansible-playbook and allows for a centralised playbook location.', prog=os.path.basename(__file__))
  subparsers = parser.add_subparsers(help='The operation to be executed')
 
# -  parser.add_argument('operation', help='The operation to be executed')
# -  parser.add_argument('playbook', default='', help='The playbook to be executed.', nargs='?')

  # create the parser for the "a" command
  parser_a = subparsers.add_parser('play', help='Execute a playbook')
  parser_a.add_argument('playbook', help='The playbook to be executed')
  parser_a.set_defaults(operation='play')

  # create the parser for the "b" command
  parser_b = subparsers.add_parser('search', help='Search for a playbook or role in our library')
  parser_b.set_defaults(operation='search')

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
    'HOSTS_PATH_DECLARATION': {'code': 4, 'title': 'There was an error in the hosts file declaration.'}
  }[err]

def check_hosts_file():
  global extra_args

  hosts_path_arg = '-i'
  cur_path_hosts = os.getcwd() + '/hosts'


  if hosts_path_arg in extra_args:
    arg_hosts_path_id = extra_args.index(hosts_path_arg) + 1
    if extra_args[arg_hosts_path_id] == None:
      sys.exist(errors('HOSTS_PATH_DECLARATION'))
    return extra_args[arg_hosts_path_id]
  elif os.path.isfile(cur_path_hosts):
    extra_args += [hosts_path_arg, cur_path_hosts]
    return cur_path_hosts
  else:
    return None

def main():
  setup_arguments()

  global args
  global extra_args

  hosts = check_hosts_file()
  if hosts:
    print 'Using hosts file located at %s' % hosts
    print
  else:
    print 'Using default system hosts file'
    print

  if(not check_conf()):
    print 'Error with environment setup.'
    sys.exit(errors('NO_SETUP')['code'])

  if(args.operation == 'search'):
    for root, dirs, files in os.walk(playbooks_path):
      for file in files:
        if file.endswith(".yml"):
          print os.path.join(root, file).replace(playbooks_path, '').lstrip('/')
    sys.exit(0)

  if(args.operation == 'play'):
    ansible_cmd = ['ansible-playbook', playbooks_path + '/' + args.playbook] + extra_args
    subprocess.call(ansible_cmd)

if __name__ == '__main__':
  main()
