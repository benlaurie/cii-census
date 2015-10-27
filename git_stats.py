#!/usr/bin/env python

import csv
import os
import re
from subprocess import check_call, check_output

def get_projects_to_analyze(filename, extra):
  '''Gets list of projects with all the details from the input file'''
  projects_to_analyze = {}
  with open(filename) as project_file:
    project_reader = csv.reader(project_file, delimiter=',')
    headers = project_reader.next()
    for project_info in project_reader:
      project_details = {}
      project_name = project_info[headers.index('Debian_Package')].strip()
      if project_name == '':
        continue
      project_details['openhub_lookup_name'] = \
             project_info[headers.index('openhub_lookup_name')].strip().lower()
      project_details['direct_network_exposure'] =\
             project_info[headers.index('direct_network_exposure')]
      project_details['process_network_data'] = \
             project_info[headers.index('process_network_data')]
      project_details['potential_privilege_escalation'] = \
             project_info[headers.index('potential_privilege_escalation')]
      project_details['comment_on_priority'] = \
             project_info[headers.index('comment_on_priority')]
      projects_to_analyze[project_name] = project_details

  with open(extra) as project_file:
    project_reader = csv.reader(project_file, delimiter=',')
    headers = project_reader.next()
    for project_info in project_reader:
      project_name = project_info[headers.index('Debian_Package')].strip()
      if project_name == '':
        continue
      projects_to_analyze[project_name]['git_repo'] = \
             project_info[headers.index('git_repo')].strip()
      
  return projects_to_analyze

class cd:
  """Context manager for changing the current working directory"""
  def __init__(self, newPath):
    self.newPath = os.path.expanduser(newPath)

  def __enter__(self):
    self.savedPath = os.getcwd()
    os.chdir(self.newPath)

  def __exit__(self, etype, value, traceback):
    os.chdir(self.savedPath)

def git_dest(repo):
  m = re.search('([^/]+)$', repo)
  r = m.group(0)
  if r.endswith('.git'):
    r = r[:-4]
  return r

def git_get(repo):
  dest = git_dest(repo)
  with cd('clones'):
    if os.path.isdir(dest):
      with cd(dest):
        check_call(['git', 'fetch'])
        check_call(['git', 'merge'])
    else:
      check_call(['git', 'clone', repo])

# Count the committers...
def git_stats(repo, when):
  dest = git_dest(repo)
  with cd('clones/' + dest):
    out = check_output(['git', 'log', '--pretty=format:%ce', '--since', when])
    #print out
    counts = {}
    for t in out.splitlines():
      if not t in counts:
        counts[t] = 1
      else:
        counts[t] += 1
    for c in sorted(counts, key=lambda c: -counts[c]):
      print c, counts[c]

def main():
  projects_to_analyze = get_projects_to_analyze('projects_to_examine.csv', 'projects-extra.csv')
  for project_name in sorted(projects_to_analyze):
    p = projects_to_analyze[project_name]
    if not 'git_repo' in p:
      continue
    repo = p['git_repo']
    print project_name, repo
    git_get(repo)
    git_stats(repo, '1 year ago')

if __name__ == "__main__":
  main()
