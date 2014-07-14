#!/usr/bin/python

# Run with:
#   python hello.py cameron
#   python hello.py


# import modules used here -- sys is a very standard one
import sys
import os

def check_conf():
  # Check that the Playbook storage is set
  playbooks_path = os.getenv('APLIB_PLAYBOOK_PATH', '~/.ansible/playbooks');
  if(not os.path.isdir(playbooks_path)):
    return 0

def errors(err):
  return {
    'NO_PLAYBOOK_DIR': {'code': 1, 'title': 'Playbook directory does not exist.'},
    'NO_SETUP': {'code': 2, 'title': 'Playbook directory does not exist.'}
  }[err]

# Gather our code in a main() function
def main():
  if(not check_conf()):
    sys.exit(errors('NO_SETUP')['code'])

  print 'Number of arguments: ', len(sys.argv)
  
  if len(sys.argv)>1:
    print '\tHello there', sys.argv[1]
  else:
    print "\tHello world!"  

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
