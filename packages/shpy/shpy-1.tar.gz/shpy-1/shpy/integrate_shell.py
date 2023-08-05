import platform
import os
from subprocess import Popen, PIPE
from time import sleep

from threading import Thread
from Queue import Queue, Empty

# Inspired by http://eyalarubas.com/python-subproc-nonblock.html
# Perpuse: making the shell non-blocking
class NonBlockingStreamReader:

    def __init__(self, stream):
        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    raise UnexpectedEndOfStream

        self._t = Thread(target = _populateQueue,
                args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None
class UnexpectedEndOfStream(Exception): pass

class background_shell():
    _pipe = None
    _nbsr_out = None
    _nbsr_err = None
    def _execute_command(self, command):
        self._pipe.stdin.write(command + os.linesep )
        
        output = ""

        while True:
            cur_output = self._nbsr_out.readline(0.1)
            # 0.1 secs to let the shell output the result
            if not cur_output:
                break
            output += cur_output
        
        err = ""
        
        while True:
            cur_err = self._nbsr_err.readline(0.1)
            # 0.1 secs to let the shell output the result
            if not cur_err:
                return err, output
            err += cur_err
        

    def command(self, c_msg):
        if c_msg.split()[0] == "cd":
            try:
                os.chdir(c_msg.split()[1])
            except:
                pass
        out = self._execute_command(c_msg)
        print out[1] #stdout 
        print out[0] #stderr


    def __init__(self):
        if platform.system() == "Windows":
            executable_path = "c:\\windows\\system32\\cmd.exe"
        else:
            executable_path = "bin/bash"
            
        self._pipe = Popen([executable_path], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
            
        self._nbsr_out = NonBlockingStreamReader(self._pipe.stdout)
        self._nbsr_err = NonBlockingStreamReader(self._pipe.stderr)

        self._execute_command("cd " + os.getcwd())                   
  