---
- hosts: all
  tasks:
  - name: Importing $variables_file
    include_vars: $variables_file

- include: $playbook
