from fabric.decorators import hosts
from fabric.context_managers import settings
from fabric.api import *

from multiprocessing import Process

def shell():
    FabricShell().run()
    
class FabricShellQueue(object):
    def __init__(self, max):
        self._max = max
        
        self._list = []
        self._running = []
        self._done = []
        
        self._finished = False
    
    def __len__(self):
        return len(self._list)
    
    def append(self, obj):
        self._list.append(obj)
        
    def start(self):
        while len(self._running) < self._max:
            self._run_process()
                
        while not self._finished:
            while len(self._running) < self._max and len(self._list) > 0:
                self._run_process()
                
            for id, job in enumerate(self._running):
                if not job.is_alive():
                    done = self._running.pop(id)
                    self._done.append(done)
                    
        
        
            if len(self._running) == 0 and len(self._list) == 0:
                self._finished = True

    def _run_process(self):
        job = self._list.pop()
        env.host_string = env.host = job.name
        job.start()
        
        self._running.append(job)

def run_multi(host, cmd, opt):
    with settings(host_string = host):
        if opt == "sudo":
            sudo(cmd)
        else:
            run(cmd)
            
class FabricShell(object):
    prompt = 'fabric::> '
    hostlist = []
        
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
                elif parts[0] == ".sudo" or parts[0] == ".msudo" or parts[0] == ".mrun":
                    self.run_cmd(line.replace(parts[0], ""), opt=parts[0][1:])
                
            elif line.strip() == "quit" or line.strip() == "exit":
                break
            else:
                self.run_cmd(line)


    def run_cmd(self, cmd, **kwargs):
        #
        # here to see if we need to cleanup thread output
        #
        threaded = False
        jobs = FabricShellQueue(3)
        
        env.user = env.local_user

        for host in env.hosts:
            with settings(host_string = host):
                #try:
                    if kwargs.has_key('opt') and kwargs['opt'] == "sudo":
                        sudo(cmd)
                    elif kwargs.has_key('opt') and kwargs['opt'] == "msudo":
                        
                        if env.password is None:
                            import getpass
                            #
                            # set the password in the env since it's UGLY to
                            # let fabric handle this if it spawns out a ton
                            # of threads for hosts
                            #
                            env.password = getpass.getpass("Sudo password: ")

                        p = Process(target=run_multi, args=(host, cmd, "sudo"))
                        p.name = host
                        jobs.append(p)
                        
                        threaded = True
                    elif kwargs.has_key('opt') and kwargs['opt'] == "mrun":
                        p = Process(target=run_multi, args=(host, cmd, "run"))
                        p.name = host
                        jobs.append(p)
                        
                        threaded = True
                        
                    else:
                        run(cmd)
                #except:
                #    print "ERROR!!!!", env.host_string
                
        if threaded:
            jobs.start()
                