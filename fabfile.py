#! coding: utf-8
# pylint: disable-msg=W0311

import fabric
from time import sleep

# Define sets of servers as roles
fabric.api.env.roledefs = {
  'master'   : ['192.168.6.126'],
}

fabric.api.env.user = 'anhpt'
fabric.api.env.warn_only = True

@fabric.api.roles('master')
def update():
  print
  print "Uploading changes..."
  print
  
  fabric.contrib.project.rsync_project(remote_dir='/home/Workspace/',
                                       exclude=['.git', '*.pyc'])

  fabric.api.run("supervisorctl -c /home/Workspace/Arl/src/supervisord.conf shutdown; sleep 1; supervisord -c /home/Workspace/Arl/src/supervisord.conf")

  
  
  
  
