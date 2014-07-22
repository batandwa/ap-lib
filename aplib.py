#!/usr/bin/python

# import modules used here -- sys is a very standard one.
import argparse
import os
import string
import subprocess
import sys
import tempfile
import yaml

from itertools import chain

# Set some defaults for the app.
playbooks_path = os.path.realpath(os.path.expanduser(os.getenv('APLIB_PLAYBOOK_PATH', '~/.ansible/playbooks')))
roles_path = os.path.realpath(os.path.expanduser(os.getenv('APLIB_ROLES_PATH', '~/.ansible/roles')))
script_dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

# So that all functions have accesss.
args = None
extra_args = None

def setup_arguments():
  # So that all functions have accesss.
  global args
  global extra_args

  # Create the top-level parser.
  parser = argparse.ArgumentParser(description='An application that calls ansible-playbook and allows for a centralised playbook location.', prog=os.path.basename(__file__))
  subparsers = parser.add_subparsers(help='The operation to be executed')
 
  # Create the parser for the "play" command.
  parser_play = subparsers.add_parser('play', help='Execute a playbook')

  # We explicitly add playbook as an argument here (instead of leaving to be handle as an addtional argument)
  # so that we can check for the playbook in multiple locations
  parser_play.add_argument('playbook', help='The playbook to be executed')
  parser_play.set_defaults(operation='play')

  # Create the parser for the "search" command.
  parser_search = subparsers.add_parser('search', help='Search for a playbook or role in our library')
  parser_search.set_defaults(operation='search')

  parser_galaxy = subparsers.add_parser('galaxy', help='A proxy command of Ansible Galaxy')
  parser_galaxy.set_defaults(operation='galaxy')

  parser_playgal = subparsers.add_parser('playgal', help='Play an Ansible Galaxy role')
  parser_playgal.set_defaults(operation='playgal')
  parser_playgal.add_argument('role', help='The role to be execute')

  # Get the arguments and additional arguments.
  args, extra_args = parser.parse_known_args()
  
# Checks taht the playbook path exists.
def check_conf():
  # Check that the Playbook storage is set.
  if(not os.path.isdir(playbooks_path)):
    return False

  return True

# Returns the error text and code give the error class.
def errors(err):
  return {
    'NO_PLAYBOOK_DIR': {'code': 1, 'title': 'Playbook directory does not exist.'},
    'NO_SETUP': {'code': 2, 'title': 'Playbook directory does not exist.'},
    'HOSTS_PATH_DECLARATION': {'code': 4, 'title': 'There was an error in the hosts file declaration.'},
    'ROLE_NOT_FOUND': {'code': 8, 'title': 'Could not find role.'}
  }[err]

# Check if the hosts file exists and returns it's name if it's not the system hosts file.
def check_hosts_file():
  # Get the additional argumants. It might have been stored there.
  global extra_args

  # The argument for the hosts file.
  hosts_path_arg = '-i'

  # The current dir path the hosts file.
  cur_path_hosts = os.getcwd() + '/hosts'

  # Check if the hosts file argument was specified in command line.
  if hosts_path_arg in extra_args:

    # Make sure the file path is passed in.
    arg_hosts_path_id = extra_args.index(hosts_path_arg) + 1
    if extra_args[arg_hosts_path_id] == None:
      sys.exist(errors('HOSTS_PATH_DECLARATION'))

    # Return the path passed.
    return extra_args[arg_hosts_path_id]

  # If the hosts file exists in the local directory.
  elif os.path.isfile(cur_path_hosts):
    extra_args += [hosts_path_arg, cur_path_hosts]
    return cur_path_hosts

  # If none was passed and there isn't one in the current directory.
  else:
    return None

def role_path(role):
  role_lib_paths = [os.getcwd() + '/' + role, roles_path + '/' + role]
  for path in role_lib_paths:
    if os.path.isfile(path) or os.path.isdir(path):
      return path

  return None

def main():
  setup_arguments()

  global args
  global extra_args

  # Check and print the location of the hosts file to be used.
  hosts = check_hosts_file()
  if hosts:
    print 'Using hosts file located at %s' % hosts
  else:
    print 'Using default system hosts file'

  # If there is an issue with the confguration and/or arguments.
  if(not check_conf()):
    print 'Error with environment setup.'
    sys.exit(errors('NO_SETUP')['code'])

  # Handle search operations.
  if(args.operation == 'search'):
    for root, dirs, files in os.walk(playbooks_path):
      for file in files:
        if file.endswith(".yml"):
          print os.path.join(root, file).replace(playbooks_path, '').lstrip('/')
    sys.exit(0)

  # Handle playbook operations
  if(args.operation == 'play'):
    # List the available playbook paths
    playbook_paths = [os.getcwd(), playbooks_path]

    # Pick the first available path
    for loc_path in playbook_paths:
      if os.path.isfile(loc_path + '/' + args.playbook):
        break
      
    full_playbook_path = loc_path + '/' + args.playbook

    if os.path.isfile(os.getcwd() + '/vars.yml'):
      print 'vars.yml file found'




      playgal_template = open(script_dir_path + 'vars_include.yml.tpl')
      playgal_template_src = string.Template(playgal_template.read())
      play = playgal_template_src.substitute({'playbook': full_playbook_path, 'variables_file': os.getcwd() + '/vars.yml'})

      playbook_f = tempfile.NamedTemporaryFile(prefix='aplib_', suffix='.yml', dir='/tmp', delete=False)
      playbook_f.write(play)
      playbook_f.flush()

      full_playbook_path = playbook_f.name


    else:
      print 'No vars.yml detected'

    ansible_cmd = ['ansible-playbook', full_playbook_path] + extra_args
    print 'Running: ' + ' '.join(ansible_cmd)
    print
    subprocess.call(ansible_cmd)

  if args.operation == 'galaxy':
    ansible_cmd = ['ansible-galaxy', '--roles-path=' + roles_path] + extra_args
    print 'Running: ' + ' '.join(ansible_cmd)
    print
    subprocess.call(ansible_cmd)

  if args.operation == 'playgal':
    found_role_path = role_path(args.role)

    if found_role_path == None:
      #  Try and install it
      ansible_cmd = ['ansible-galaxy', '--roles-path=' + roles_path, 'install', args.role]
      print 'Running: ' + ' '.join(ansible_cmd)
      subprocess.call(ansible_cmd)
      
      found_role_path = role_path(args.role)
      if found_role_path == None:
        err = errors('ROLE_NOT_FOUND')
        print err['title']
        sys.exit(err['code'])

    playgal_template = open(script_dir_path + 'playgal.yml.tpl')
    playgal_template_src = string.Template(playgal_template.read())
    play = playgal_template_src.substitute({'roles': found_role_path})

    playbook_f = tempfile.NamedTemporaryFile(prefix='aplib_', suffix='.yml', dir='/tmp', delete=False)
    playbook_f.write(play)
    playbook_f.flush()
     
    ansible_cmd = ['ansible-playbook', playbook_f.name] + extra_args
    print 'Running: ' + ' '.join(ansible_cmd)
    print
    subprocess.call(ansible_cmd)

if __name__ == '__main__':
  main()
