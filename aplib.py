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
args = None

def setup_arguments():
  global args

  parser = argparse.ArgumentParser(description='An application that calls ansible-playbook and allows for a centralised playbook location.')
  # parser.add_argument('--discover')
  parser.add_argument('--discover', action='store_true', help='List playbooks that exist in the library path.')
  parser.add_argument('playbook', help='The playbook to be executed.')
  args = parser.parse_args()
  
def check_conf():
  # Check that the Playbook storage is set
  if(not os.path.isdir(playbooks_path)):
    return False

  return True

def errors(err):
  return {
    'NO_PLAYBOOK_DIR': {'code': 1, 'title': 'Playbook directory does not exist.'},
    'NO_SETUP': {'code': 2, 'title': 'Playbook directory does not exist.'}
  }[err]

# Gather our code in a main() function
def main():
  setup_arguments()
  global args

  if(not check_conf()):
    sys.exit(errors('NO_SETUP')['code'])

  arguments = sys.argv
  del arguments[0];
  
  if(arguments[0] == args.discover):
    for root, dirs, files in os.walk(playbooks_path):
      for file in files:
        if file.endswith(".yml"):
          print os.path.join(root, file).replace(playbooks_path, '').lstrip('/')
    sys.exit(0)

  subprocess.call(['ansible-playbook', playbooks_path + '/' + args.playbook])
  # subprocess.call('ansible ' + sys.argv[1])
  # print 'Number of arguments: ', len(sys.argv)
  # if len(sys.argv)>1:
  #   print '\tHello there', sys.argv[1]
  # else:
  #   print "\tHello world!"  

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()
