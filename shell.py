from fabric.decorators import hosts
from fabric.context_managers import settings
from fabric.api import *

import readline

def shell():
    FabricShell().run()
    
class FabricShell(object):
    prompt = 'fabric::> '
        
    def run(self):
        while True:
            line = raw_input(self.prompt)
            
            #
            # checking first line if we are running a special command
            #
            if line.strip() == "":
                continue
            elif line[0] == ".":
                parts = line.split()
                if len(parts) == 1:
                    continue
                
                if parts[0] == ".sudo":
                    self.run_cmd(line.replace(".sudo", ""), opt="sudo")
                
            elif line.strip() == "quit":
                break
            else:
                self.run_cmd(line)


    def run_cmd(self, cmd, **kwargs):
        env.user = env.local_user

        for host in env.hosts:
            with settings(host_string = host):
                if kwargs.has_key('opt') and kwargs['opt'] == "sudo":
                    sudo(cmd)
                else:
                    run(cmd)